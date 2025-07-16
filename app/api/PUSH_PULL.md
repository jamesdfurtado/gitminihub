# Before anything! Remote adds

In order for GitMini to login to a CLI session, there already needs to be a .gitmini folder.
The idea is that the user does "gitmini init" --> "gitmini login" --> "gitmini remote add <repo-name>".

We need to create the endpois for "gitmini remote add" command.
* This command basically just means that we are connecting our local repository to the remote repository.
* Then from there, the user will push their stuff up to it.
* For now, we will not do any pulls, just pushes. This means users cannot modify their remote repo from GitMiniHub.

When the user calls "gitmini remote add <repo-name>", it does:

POST /api/remote/add
{
  "user": "james",
  "api_key": "abc123xyz",
  "repo": "my-repo"
}

Responses:

Success
{
  "status": "ok",
  "message": "Connected to remote",
  "branches": {
    "main": "abc123...",
    "dev": "def456..."      // This part is crucial for filling in our remote_branches.json properly.
  }
}

Auth Failure
{
  "status": "error",
  "message": "Authentication failed"
}

Repo not found
{
  "status": "error",
  "message": "Repository not found"
}

Repo exists, but is someone elses. (This should NEVER be the case, 
because when we are connecting to repos, you can only connect to your own)
{
  "status": "error",
  "message": "Access denied to repository"
}

Malformed Payload
{
  "status": "error",
  "message": "Invalid request payload"
}



---

General thing: Make sure the body request format is pre-determined

# Push

When GitMini CLI makes a push, we do:

"POST /api/remote/push", with the following payload:

{
  "user": "james",
  "api_key": "abc123xyz",
  "repo": "my-repo",
  "branch": "main",

  "last_known_remote_commit": "def456...",
  "new_commit": "abc123..."
}


and an attached "new_objects.tar.gz" compressed file, which contains
ONLY the new objects needed.

Responses:

Successful push:
{
  "status": "ok",
  "message": "Push successful",
  "updated_head": "abc123..."  // matches new_commit
}
Updated head field should be then used to update the associated commit in the local remote_branch.json


rejected- non-fast forward push.
This happens when last_known_remote_commit does not match the current commit at refs/heads/<branch>
on the server.
{
  "status": "error",
  "message": "Non-fast-forward push rejected. Remote branch has diverged.",
  "remote_head": "ghi789..."  // actual current head
}

Could not find specified branch
{
  "status": "error",
  "message": "Remote branch not found.",
  "remote_head": "ghi789..."  // actual current head
}

Auth failure
{
  "status": "error",
  "message": "Authentication failed"
}

Repo not found or unauthorized access
{
  "status": "error",
  "message": "Repository not found or access denied"
}

Malformed Payload
{
  "status": "error",
  "message": "Invalid push payload"
}

Corrupt or Missing Archive file (if new_objects.tar.gz is missing/unreadable)
{
  "status": "error",
  "message": "Object archive missing or corrupt"
}


---

# Pull

IGNORE THIS SECTION FOR NOW, WE ARE JUST GOING TO IMPLEMENT PUSH.

When GitMini CLI requests a pull, we do:

POST /api/remote/pull

{
    user,
    api_key,
    repo,
    branch
    
    last_local_commit   # this hash is fetched directly from refs/heads/<current_local_branch>
}

Upon success, you get response:

{
    "new_commit" : <hash>
}
as well as an attached "missing_objects.tar.gz", which contains only new needed files. 
(the new commit, its associated tree, and new blobs)