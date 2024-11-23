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
        
    def get_followers(self, actor):
        """Get complete list of followers for an actor"""
        followers = []
        cursor = None
        
        while True:
            response = self.client.app.bsky.graph.get_followers({
                'actor': actor,
                'limit': 100,
                'cursor': cursor
            })
            
            followers.extend([(f.did, f.handle) for f in response.followers])
            
            if not response.cursor:
                break
            cursor = response.cursor
            
        return followers
        
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
        
    def follow_friends_followers(self, friend_handle):
        """Follow the followers of a specified friend"""
        print(f"Fetching followers of @{friend_handle}...")
        
        # Get list of accounts you already follow
        my_follows = self.get_my_follows()
        print(f"You currently follow {len(my_follows)} accounts")
        
        # Get friend's followers
        followers = self.get_followers(friend_handle)
        print(f"@{friend_handle} has {len(followers)} followers")
        
        # Filter out accounts you already follow
        new_follows = [(did, handle) for did, handle in followers if did not in my_follows]
        print(f"Found {len(new_follows)} accounts you don't already follow")
        
        # Follow each account
        for i, (did, handle) in enumerate(new_follows, 1):
            try:
                print(f"[{i}/{len(new_follows)}] Attempting to follow @{handle}")
                self.client.app.bsky.graph.follow.create(
                    repo=self.client.me.did,
                    record={'subject': did, 'createdAt': time.strftime('%Y-%m-%dT%H:%M:%SZ')}
                )
                print(f"Successfully followed @{handle}")
                
                # 6 second delay between follows
                time.sleep(6)
                
            except Exception as e:
                print(f"Error following @{handle}: {str(e)}")

def main():
    # Replace with your credentials
    manager = BlueskyFollowerFinder("pdennis.research@gmail.com", "RjU9!0gDH!GCxwvx")
    
    try:
        manager.login()
        
        # Get the friend's handle from user input
        friend = input("Enter your friend's handle (without the @): ")
        manager.follow_friends_followers(friend)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
