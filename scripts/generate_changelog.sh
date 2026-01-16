#!/usr/bin/env bash
# Generate CHANGELOG.md from git commits
# Uses conventional commit format when available

set -e

# Check bash version for associative arrays (bash 4+)
if [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
    # Use fallback for bash 3.x (macOS default)
    USE_ASSOCIATIVE_ARRAYS=false
else
    USE_ASSOCIATIVE_ARRAYS=true
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get version from pyproject.toml
get_version() {
    grep '^version = ' pyproject.toml | cut -d'"' -f2
}

# Get all tags sorted by version
get_tags() {
    git tag -l "v*" | sort -V
}

# Get commits between two tags (or from tag to HEAD)
get_commits() {
    local from=$1
    local to=${2:-HEAD}

    if [ -z "$from" ]; then
        # First release - all commits
        git log --pretty=format:"%h|%s|%an|%ad" --date=short
    else
        # Between tags
        git log "$from..$to" --pretty=format:"%h|%s|%an|%ad" --date=short
    fi
}

# Categorize commit based on message
categorize_commit() {
    local message=$1

    # Conventional commits
    if [[ $message =~ ^feat:.*|^feature:.* ]]; then
        echo "features"
    elif [[ $message =~ ^fix:.* ]]; then
        echo "fixes"
    elif [[ $message =~ ^docs:.* ]]; then
        echo "documentation"
    elif [[ $message =~ ^test:.* ]]; then
        echo "tests"
    elif [[ $message =~ ^refactor:.* ]]; then
        echo "refactoring"
    elif [[ $message =~ ^chore:.* ]]; then
        echo "chores"
    elif [[ $message =~ ^[Aa]dd.* ]]; then
        echo "features"
    elif [[ $message =~ ^[Ff]ix.* ]]; then
        echo "fixes"
    elif [[ $message =~ ^[Uu]pdate.* ]]; then
        echo "changes"
    elif [[ $message =~ ^[Rr]emove.* ]]; then
        echo "removals"
    else
        echo "other"
    fi
}

# Clean commit message
clean_message() {
    local message=$1

    # Remove conventional commit prefix
    message=$(echo "$message" | sed -E 's/^(feat|fix|docs|test|refactor|chore|feature):\s*//')

    # Remove emoji at start (like 🤖)
    message=$(echo "$message" | sed -E 's/^[[:space:]]*[^\x00-\x7F]+[[:space:]]*//')

    # Capitalize first letter
    message="$(echo "${message:0:1}" | tr '[:lower:]' '[:upper:]')${message:1}"

    echo "$message"
}

# Generate changelog for a version
generate_version_changelog() {
    local version=$1
    local from_tag=$2
    local to_tag=$3
    local date=$4

    echo ""
    echo "## [$version] - $date"
    echo ""

    # Variables to hold commits by category (bash 3.x compatible)
    features=""
    fixes=""
    changes=""
    documentation=""
    refactoring=""
    tests=""
    removals=""
    chores=""
    other=""

    # Process commits
    while IFS='|' read -r hash message author commit_date; do
        # Skip merge commits
        if [[ $message =~ ^Merge.* ]]; then
            continue
        fi

        # Skip version bump commits
        if [[ $message =~ ^Bump[[:space:]]version.* ]]; then
            continue
        fi

        # Categorize
        category=$(categorize_commit "$message")
        cleaned_message=$(clean_message "$message")

        # Add to appropriate category
        case "$category" in
            features)
                [ -n "$features" ] && features+=$'\n'
                features+="- $cleaned_message (\`$hash\`)"
                ;;
            fixes)
                [ -n "$fixes" ] && fixes+=$'\n'
                fixes+="- $cleaned_message (\`$hash\`)"
                ;;
            changes)
                [ -n "$changes" ] && changes+=$'\n'
                changes+="- $cleaned_message (\`$hash\`)"
                ;;
            documentation)
                [ -n "$documentation" ] && documentation+=$'\n'
                documentation+="- $cleaned_message (\`$hash\`)"
                ;;
            refactoring)
                [ -n "$refactoring" ] && refactoring+=$'\n'
                refactoring+="- $cleaned_message (\`$hash\`)"
                ;;
            tests)
                [ -n "$tests" ] && tests+=$'\n'
                tests+="- $cleaned_message (\`$hash\`)"
                ;;
            removals)
                [ -n "$removals" ] && removals+=$'\n'
                removals+="- $cleaned_message (\`$hash\`)"
                ;;
            chores)
                [ -n "$chores" ] && chores+=$'\n'
                chores+="- $cleaned_message (\`$hash\`)"
                ;;
            *)
                [ -n "$other" ] && other+=$'\n'
                other+="- $cleaned_message (\`$hash\`)"
                ;;
        esac
    done < <(get_commits "$from_tag" "$to_tag")

    # Print categories
    if [ -n "$features" ]; then
        echo "### ✨ Features"
        echo ""
        echo "$features"
        echo ""
    fi

    if [ -n "$fixes" ]; then
        echo "### 🐛 Bug Fixes"
        echo ""
        echo "$fixes"
        echo ""
    fi

    if [ -n "$changes" ]; then
        echo "### 🔄 Changes"
        echo ""
        echo "$changes"
        echo ""
    fi

    if [ -n "$documentation" ]; then
        echo "### 📚 Documentation"
        echo ""
        echo "$documentation"
        echo ""
    fi

    if [ -n "$refactoring" ]; then
        echo "### ♻️ Refactoring"
        echo ""
        echo "$refactoring"
        echo ""
    fi

    if [ -n "$removals" ]; then
        echo "### 🗑️ Removals"
        echo ""
        echo "$removals"
        echo ""
    fi

    if [ -n "$tests" ]; then
        echo "### ✅ Tests"
        echo ""
        echo "$tests"
        echo ""
    fi

    if [ -n "$chores" ]; then
        echo "### 🔧 Chores"
        echo ""
        echo "$chores"
        echo ""
    fi

    if [ -n "$other" ]; then
        echo "### Other Changes"
        echo ""
        echo "$other"
        echo ""
    fi
}

# Generate full changelog
generate_changelog() {
    local output_file="CHANGELOG.md"

    echo -e "${BLUE}[INFO]${NC} Generating changelog..."

    # Start changelog
    {
        echo "# Changelog"
        echo ""
        echo "All notable changes to Hrisa Docs will be documented in this file."
        echo ""
        echo "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),"
        echo "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)."

        # Get all tags
        TAGS=($(get_tags))

        if [ ${#TAGS[@]} -eq 0 ]; then
            # No tags yet - generate for current version
            CURRENT_VERSION=$(get_version)
            CURRENT_DATE=$(date +%Y-%m-%d)
            generate_version_changelog "$CURRENT_VERSION" "" "HEAD" "$CURRENT_DATE"
        else
            # Generate for each tag
            for i in "${!TAGS[@]}"; do
                TAG=${TAGS[$i]}
                VERSION=${TAG#v}  # Remove 'v' prefix

                # Get date of tag
                TAG_DATE=$(git log -1 --format=%ad --date=short "$TAG")

                # Determine previous tag
                if [ $i -eq 0 ]; then
                    PREV_TAG=""
                else
                    PREV_TAG=${TAGS[$((i-1))]}
                fi

                generate_version_changelog "$VERSION" "$PREV_TAG" "$TAG" "$TAG_DATE"
            done

            # Check for unreleased commits
            LATEST_TAG=${TAGS[-1]}
            UNRELEASED_COUNT=$(git log "$LATEST_TAG..HEAD" --oneline | wc -l)

            if [ "$UNRELEASED_COUNT" -gt 0 ]; then
                echo ""
                echo "## [Unreleased]"
                echo ""
                echo "### Changes since $LATEST_TAG"
                echo ""

                # Show unreleased commits
                git log "$LATEST_TAG..HEAD" --pretty=format:"- %s (\`%h\`)" | grep -v "^- Merge"
                echo ""
            fi
        fi

        # Footer
        echo ""
        echo "---"
        echo ""
        echo "**Legend:**"
        echo "- ✨ Features: New functionality"
        echo "- 🐛 Bug Fixes: Bugs that were fixed"
        echo "- 🔄 Changes: Updates to existing features"
        echo "- 📚 Documentation: Documentation improvements"
        echo "- ♻️ Refactoring: Code improvements without changing functionality"
        echo "- 🗑️ Removals: Deprecated or removed features"
        echo "- ✅ Tests: Test additions or improvements"
        echo "- 🔧 Chores: Maintenance tasks"

    } > "$output_file"

    echo -e "${GREEN}[SUCCESS]${NC} Changelog generated: $output_file"
}

# Main
main() {
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║  Hrisa Docs - Changelog Generator     ║"
    echo "╚════════════════════════════════════════╝"
    echo ""

    generate_changelog

    echo ""
    echo "Review the generated CHANGELOG.md file"
}

main "$@"
