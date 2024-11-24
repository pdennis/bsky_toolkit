from atproto import Client
import time

class BlueskyFollowerFinder:
    def __init__(self, email, password):
        self.client = Client()
        self.email = email
        self.password = password
        
    def login(self):
        """Log in to Bluesky"""
        self.client.login(self.email, self.password)
        
    def get_followers_chunk(self, actor, chunk_size=100):
        """Get a chunk of followers and the cursor for the next chunk"""
        response = self.client.app.bsky.graph.get_followers({
            'actor': actor,
            'limit': chunk_size
        })
        
        followers = [(f.did, f.handle) for f in response.followers]
        next_cursor = response.cursor
        
        return followers, next_cursor
        
    def get_my_follows(self):
        """Get list of DIDs that you already follow"""
        follows = set()
        cursor = None
        
        while True:
            response = self.client.app.bsky.graph.get_follows({
                'actor': self.client.me.did,
                'limit': 100,
                'cursor': cursor
            })
            
            follows.update(f.did for f in response.follows)
            
            if not response.cursor:
                break
            cursor = response.cursor
            
        return follows
        
    def follow_friends_followers_chunked(self, friend_handle, chunk_size=100):
        """Follow the followers of a specified friend in chunks"""
        print(f"Getting your current follows...")
        my_follows = self.get_my_follows()
        print(f"You currently follow {len(my_follows)} accounts")
        
        cursor = None
        chunk_num = 1
        
        while True:
            print(f"\nFetching chunk {chunk_num} of @{friend_handle}'s followers...")
            
            try:
                # Get next chunk of followers
                if cursor:
                    response = self.client.app.bsky.graph.get_followers({
                        'actor': friend_handle,
                        'limit': chunk_size,
                        'cursor': cursor
                    })
                else:
                    response = self.client.app.bsky.graph.get_followers({
                        'actor': friend_handle,
                        'limit': chunk_size
                    })
                
                followers = [(f.did, f.handle) for f in response.followers]
                cursor = response.cursor
                
                # Filter out accounts you already follow
                new_follows = [(did, handle) for did, handle in followers if did not in my_follows]
                
                print(f"Found {len(new_follows)} new accounts in this chunk")
                
                if new_follows:
                    # Ask if user wants to process this chunk
                    choice = input(f"Process these {len(new_follows)} accounts? (y/n/q to quit): ").lower()
                    
                    if choice == 'q':
                        print("Quitting...")
                        break
                    elif choice == 'y':
                        # Follow accounts in this chunk
                        for i, (did, handle) in enumerate(new_follows, 1):
                            try:
                                print(f"[{i}/{len(new_follows)}] Attempting to follow @{handle}")
                                self.client.app.bsky.graph.follow.create(
                                    repo=self.client.me.did,
                                    record={'subject': did, 'createdAt': time.strftime('%Y-%m-%dT%H:%M:%SZ')}
                                )
                                print(f"Successfully followed @{handle}")
                                my_follows.add(did)  # Add to our follow list so we don't try again
                                
                                # 6 second delay between follows
                                time.sleep(6)
                                
                            except Exception as e:
                                print(f"Error following @{handle}: {str(e)}")
                
                if not cursor:
                    print("\nNo more followers to process!")
                    break
                    
                chunk_num += 1
                
            except Exception as e:
                print(f"Error fetching followers: {str(e)}")
                break

def main():
    # Replace with your credentials
    manager = BlueskyFollowerFinder("pdennis.research@gmail.com", "RjU9!0gDH!GCxwvx")
    
    try:
        manager.login()
        
        # Get the friend's handle from user input
        friend = input("Enter your friend's handle (without the @): ")
        chunk_size = input("How many followers to fetch per chunk? (default 100): ")
        chunk_size = int(chunk_size) if chunk_size.isdigit() else 100
        
        manager.follow_friends_followers_chunked(friend, chunk_size)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()