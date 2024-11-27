from atproto import Client
import time
from urllib.parse import urlparse
from bluesky_db import BlueskyDB

class BlueskyFollowerManager:
    def __init__(self, email, password):
        self.client = Client()
        self.email = email
        self.password = password
        self.db = BlueskyDB()
        
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
            
            followers.extend([f.did for f in response.followers])
            
            if not response.cursor:
                break
            cursor = response.cursor
            
        return followers
        
    def get_follows(self, actor):
        """Get complete list of accounts the actor follows with their viewer state"""
        follows = []
        cursor = None
        
        while True:
            response = self.client.app.bsky.graph.get_follows({
                'actor': actor,
                'limit': 100,
                'cursor': cursor
            })
            
            for follow in response.follows:
                if hasattr(follow.viewer, 'following'):
                    follows.append((follow.did, follow.viewer.following))
            
            if not response.cursor:
                break
            cursor = response.cursor
            
        return follows
        
    def parse_at_uri(self, uri):
        """Parse an AT URI into repo and rkey components"""
        parts = uri.split('/')
        return parts[2], parts[-1]
        
    def unfollow_non_followers(self):
        """Unfollow accounts that don't follow back"""
        profile = self.client.app.bsky.actor.get_profile({'actor': self.client.me.did})
        
        followers = self.get_followers(profile.did)
        follows = self.get_follows(profile.did)
        
        follow_uris = {did: uri for did, uri in follows if uri is not None}
        
        following_dids = set(follow_uris.keys())
        follower_dids = set(followers)
        non_mutual = following_dids - follower_dids
        
        print(f"You follow {len(following_dids)} accounts")
        print(f"You have {len(followers)} followers")
        print(f"Found {len(non_mutual)} non-mutual follows")
        
        for did in non_mutual:
            try:
                profile = self.client.app.bsky.actor.get_profile({'actor': did})
                print(f"Attempting to unfollow @{profile.handle}")
                
                follow_uri = follow_uris.get(did)
                if follow_uri:
                    repo, rkey = self.parse_at_uri(follow_uri)
                    success = self.client.app.bsky.graph.follow.delete(repo, rkey)
                    if success:
                        # Record the unfollow in database
                        self.db.add_unfollowed_account(did, profile.handle)
                        print(f"Successfully unfollowed @{profile.handle}")
                    else:
                        print(f"Failed to unfollow @{profile.handle}")
                else:
                    print(f"Could not find follow URI for @{profile.handle}")
                
                time.sleep(3.5)
                
            except Exception as e:
                print(f"Error unfollowing {did}: {str(e)}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

def main():
    with BlueskyFollowerManager("pdennis.research@gmail.com", "RjU9!0gDH!GCxwvx") as manager:
        try:
            manager.login()
            manager.unfollow_non_followers()
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()