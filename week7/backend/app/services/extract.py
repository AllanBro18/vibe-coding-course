import re
from typing import List


def extract_action_items(text: str) -> List[str]:
    """Extract likely action items from freeform text with enhanced pattern recognition."""
    
    lines = [line.strip("- *") for line in text.splitlines() if line.strip()]
    results: List[str] = []
    
    # Expanded action verbs and keywords
    action_verbs = {
        # Core actions
        "fix", "implement", "review", "refactor", "write", "add", "update", "remove",
        "create", "build", "test", "deploy", "merge", "commit", "push", "pull",
        "configure", "setup", "install", "upgrade", "migrate", "backup", "restore",
        "validate", "verify", "check", "audit", "monitor", "track", "follow",
        "schedule", "plan", "organize", "coordinate", "manage", "handle", "process",
        "resolve", "address", "solve", "investigate", "analyze", "research", "explore",
        
        # Communication
        "contact", "email", "call", "message", "notify", "inform", "discuss", "meet",
        "present", "document", "report", "summarize", "explain", "clarify",
        
        # Project management
        "assign", "delegate", "prioritize", "schedule", "deadline", "due", "complete",
        "finish", "deliver", "submit", "approve", "reject", "review", "sign-off",
    }
    
    # Priority and urgency indicators
    priority_keywords = {
        "urgent", "asap", "immediately", "critical", "high priority", "important",
        "deadline", "due soon", "overdue", "blocking", "showstopper", "emergency"
    }
    
    # Time-related patterns
    time_patterns = [
        r'\b(by|before|after|on|at)\s+\d{1,2}[:/]\d{2}',  # by 5:00, before 3/15
        r'\b(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
        r'\b(this|next)\s+(week|month|quarter|year)\b',
        r'\b\d+\s+(days?|weeks?|months?|hours?|minutes?)\b',
        r'\b(end|middle|beginning)\s+of\s+(week|month|quarter|year)\b',
    ]
    
    # Question patterns that indicate actions
    question_patterns = [
        r'\b(should|can|could|will|would|do|does|are|is)\s+(we|i|you|they)\b',
        r'\b(need|want|require)\s+(to|i|you|we|they)\b',
        r'\b(what|how|when|where|who)\s+(should|can|will|do)\b',
    ]
    
    # Assignment patterns
    assignment_patterns = [
        r'@\w+',  # @username
        r'\b(assign(ed)?\s+to|responsible|owner|assignee)\b',
    ]
    
    for raw_line in lines:
        line = raw_line.strip()
        normalized = line.lower()
        
        # Skip very short lines or lines that are clearly not actions
        if len(line) < 3 or normalized in {"notes", "comments", "summary", "overview"}:
            continue
            
        # 1. Explicit markers (highest priority)
        if (normalized.startswith(("todo:", "action:", "task:", "fixme:", "hack:")) or
            normalized.endswith("!") or
            "todo" in normalized or "action item" in normalized):
            results.append(line)
            continue
            
        # 2. Checkbox-style tasks
        if (normalized.startswith(("[ ]", "[x]", "[✓]", "☐", "☑", "- [ ]", "- [x]")) or
            re.search(r'\[[\sx]\]', normalized)):
            results.append(line)
            continue
            
        # 3. Priority indicators
        if any(keyword in normalized for keyword in priority_keywords):
            results.append(line)
            continue
            
        # 4. Time-based patterns
        if any(re.search(pattern, normalized) for pattern in time_patterns):
            results.append(line)
            continue
            
        # 5. Assignment patterns
        if any(re.search(pattern, normalized) for pattern in assignment_patterns):
            results.append(line)
            continue
            
        # 6. Question patterns indicating actions
        if any(re.search(pattern, normalized) for pattern in question_patterns):
            results.append(line)
            continue
            
        # 7. Conditional actions (if/when/after/before)
        if re.search(r'\b(if|when|after|before|once|unless)\s+', normalized):
            results.append(line)
            continue
            
        # 8. Numbered or bulleted lists with action verbs
        parts = normalized.split(maxsplit=1)
        if not parts:
            continue
            
        first_token = parts[0]
        maybe_rest = parts[1] if len(parts) > 1 else ""
        
        # Handle numbered/bulleted lists
        if (first_token.endswith((".", ")", "]", ":")) and maybe_rest) or first_token in {"*", "-", "•"}:
            first_word = maybe_rest.split(maxsplit=1)[0] if maybe_rest else ""
        else:
            first_word = first_token
            
        # Check if first word is an action verb
        if first_word in action_verbs:
            results.append(line)
            continue
            
        # 9. Sentences starting with action verbs (more flexible)
        words = normalized.split()
        if words and words[0] in action_verbs:
            results.append(line)
            continue
            
        # 10. Look for imperative sentences (commands)
        # Sentences that start with verbs in imperative form
        if (len(words) >= 2 and 
            not normalized.startswith(("the", "a", "an", "this", "that", "these", "those", "i", "we", "you", "he", "she", "it", "they")) and
            not any(word in normalized for word in {"is", "are", "was", "were", "has", "have", "had"})):
            # Additional check: contains action-related words
            action_indicators = action_verbs | {"must", "should", "need", "have to", "required"}
            if any(indicator in normalized for indicator in action_indicators):
                results.append(line)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_results = []
    for item in results:
        normalized_item = item.lower().strip()
        if normalized_item not in seen:
            seen.add(normalized_item)
            unique_results.append(item)
    
    return unique_results

    return results
