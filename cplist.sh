#!/bin/bash
# Basic shell script for Revibot II Community Portal list update
# This script is free software; licensed under GPLv3 or later.
# Login is handled by BotPassword.

cd revibot # Go to pywikibot core
python3 ../core/pwb.py community_portal_list # Actual scripts - clean the sandbox.
