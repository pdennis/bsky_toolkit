from atproto import Client
import time
from bluesky_db import BlueskyDB

class BlueskyFollowerFinder:
    def __init__(self, email, password):
        self.client = Client()
        self.email = email
        self.password = password
        self.db = BlueskyDB()
        
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
        total_processed = 0
        skipped_previously_unfollowed = 0
        
        print(f"\nStarting to process @{friend_handle}'s followers in chunks of {chunk_size}...")
        print("Press Ctrl+C at any time to stop the script safely\n")
        
        try:
            while True:
                try:
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
                    
                    # Filter out accounts you already follow and previously unfollowed
                    new_follows = []
                    for did, handle in followers:
                        if did in my_follows:
                            continue
                        if self.db.is_previously_unfollowed(did):
                            skipped_previously_unfollowed += 1
                            continue
                        new_follows.append((did, handle))
                    
                    print(f"\nChunk {chunk_num}: Found {len(new_follows)} new accounts to follow")
                    if skipped_previously_unfollowed > 0:
                        print(f"Skipped {skipped_previously_unfollowed} previously unfollowed accounts")
                    
                    if new_follows:
                        for i, (did, handle) in enumerate(new_follows, 1):
                            try:
                                print(f"[Chunk {chunk_num}, {i}/{len(new_follows)}] Following @{handle}")
                                self.client.app.bsky.graph.follow.create(
                                    repo=self.client.me.did,
                                    record={'subject': did, 'createdAt': time.strftime('%Y-%m-%dT%H:%M:%SZ')}
                                )
                                my_follows.add(did)
                                total_processed += 1
                                
                                time.sleep(6)
                                
                            except Exception as e:
                                print(f"Error following @{handle}: {str(e)}")
                    
                    if not cursor:
                        print("\nCompleted! No more followers to process.")
                        print(f"Total accounts followed: {total_processed}")
                        print(f"Total previously unfollowed accounts skipped: {skipped_previously_unfollowed}")
                        break
                        
                    chunk_num += 1
                    
                except Exception as e:
                    print(f"Error fetching followers: {str(e)}")
                    break
                    
        except KeyboardInterrupt:
            print("\n\nScript stopped by user.")
            print(f"Total accounts followed before stopping: {total_processed}")
            print(f"Total previously unfollowed accounts skipped: {skipped_previously_unfollowed}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

def main():
    with BlueskyFollowerFinder("pdennis.research@gmail.com", "RjU9!0gDH!GCxwvx") as manager:
        try:
            manager.login()
            
            friend = input("Enter your friend's handle (without the @): ")
            chunk_size = input("How many followers to fetch per chunk? (default 100): ")
            chunk_size = int(chunk_size) if chunk_size.isdigit() else 100
            
            manager.follow_friends_followers_chunked(friend, chunk_size)
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()