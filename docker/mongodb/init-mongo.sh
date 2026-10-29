#!/usr/bin/env bash
set -e

mongosh -- "$MONGO_INITDB_DATABASE" <<EOF
const rootUser = '$MONGO_INITDB_ROOT_USERNAME';
const rootPass = '$MONGO_INITDB_ROOT_PASSWORD';
const targetDb = '$MONGO_INITDB_DATABASE';
const authSourceDb = '${MONGODB_AUTH_SOURCE:-assistant_medixa}';

const adminDb = db.getSiblingDB('admin');
adminDb.auth(rootUser, rootPass);

const appDb = db.getSiblingDB(authSourceDb);
if (!appDb.getUser(rootUser)) {
  appDb.createUser({
    user: rootUser,
    pwd: rootPass,
    roles: [
      { role: 'readWrite', db: targetDb },
      { role: 'dbAdmin', db: targetDb }
    ]
  });
}
EOF
