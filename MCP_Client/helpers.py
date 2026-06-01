import json

class DebugList(list):
    def __init__(self, *args, debug=True):
        super().__init__(*args)
        self.debug = debug

    def append(self, item):
        super().append(item)
        if self.debug:
            self._metadata_print(item)

    def _metadata_print(self, msg):
        if not isinstance(msg, dict) or 'role' not in msg:
            print(f"🪲 [RAW PAYLOAD]: {msg}")
            return

        role = msg.get('role', 'unknown').upper()
        role += ' 😎' if role == 'USER' else ' 🤖'        
        content = msg.get('content', [])

        # ANSI styling for structural visibility
        BOLD = "\033[1m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        print(f"\n{BOLD}{BLUE}[METADATA LAYER] ─── Message Object ────────────────────────────────────{RESET}")
        print(f" ├── {BOLD}Role:{RESET} {MAGENTA}{role}{RESET}")
        print(f" └── {BOLD}Content Blocks (Total: {len(content) if isinstance(content, list) else 1}):{RESET}")

        if isinstance(content, str):
            print(f"      ├── {YELLOW}[Block Type]: Raw String Fallback{RESET}")
            print(f"      └── [Payload]: {content}")
            print(f"{BOLD}{BLUE}────────────────────────────────────────────────────────────────────────{RESET}\n")
            return

        for idx, block in enumerate(content):
            is_last_block = (idx == len(content) - 1)
            block_prefix = "      └──" if is_last_block else "      ├──"
            inner_prefix = "         " if is_last_block else "      │  "

            block_type = getattr(block, 'type', None) if not isinstance(block, dict) else block.get('type')
            
            print(f"{block_prefix} {BOLD}{CYAN}[Block #{idx} Type]: {block_type.upper()}{RESET}")

            # ─── CASE A: TEXT BLOCK ───
            if block_type == 'text':
                text = getattr(block, 'text', '') if not isinstance(block, dict) else block.get('text', '')
                print(f"{inner_prefix}├── {BOLD}[Data]:{RESET} plain_text")
                # Truncate content preview to keep focus on metadata structure
                preview = text.replace('\n', ' ')
                if len(preview) > 80:
                    preview = preview[:77] + "..."
                print(f"{inner_prefix}└── {BOLD}[Preview]:{RESET} \"{preview}\"")

            # ─── CASE B: TOOL USE BLOCK ───
            elif block_type == 'tool_use':
                name = getattr(block, 'name', '') if not isinstance(block, dict) else block.get('name', '')
                tool_id = getattr(block, 'id', '') if not isinstance(block, dict) else block.get('id', '')
                tool_input = getattr(block, 'input', {}) if not isinstance(block, dict) else block.get('input', {})
                
                print(f"{inner_prefix}├── {BOLD}Tool Name:{RESET} {GREEN}{name}{RESET}")
                print(f"{inner_prefix}├── {BOLD}Execution ID:{RESET} {tool_id}")
                print(f"{inner_prefix}└── {BOLD}Arguments Schema (JSON Input):{RESET}")
                try:
                    pretty_input = json.dumps(tool_input, indent=2, ensure_ascii=False)
                    for line in pretty_input.splitlines():
                        print(f"{inner_prefix}    {line}")
                except Exception:
                    print(f"{inner_prefix}    {tool_input}")

            # ─── CASE C: TOOL RESULT BLOCK ───
            elif block_type == 'tool_result':
                tool_id = getattr(block, 'tool_use_id', '') if not isinstance(block, dict) else block.get('tool_use_id', '')
                raw_content = getattr(block, 'content', '') if not isinstance(block, dict) else block.get('content', '')
                
                print(f"{inner_prefix}├── {BOLD}Responding To ID:{RESET} {tool_id}")
                print(f"{inner_prefix}└── {BOLD}Execution Output (JSON/String Result):{RESET}")
                try:
                    if isinstance(raw_content, str):
                        parsed_content = json.loads(raw_content)
                    else:
                        parsed_content = raw_content
                    pretty_result = json.dumps(parsed_content, indent=2, ensure_ascii=False)
                    for line in pretty_result.splitlines()[:12]: # Show first 12 lines for layout control
                        print(f"{inner_prefix}    {line}")
                    if len(pretty_result.splitlines()) > 12:
                        print(f"{inner_prefix}    ... ({len(pretty_result.splitlines()) - 12} metadata lines hidden)")
                except Exception:
                    lines = str(raw_content).splitlines()
                    for line in lines[:6]:
                        print(f"{inner_prefix}    {line}")
                    if len(lines) > 6:
                        print(f"{inner_prefix}    ... (truncated raw text)")

        print(f"{BOLD}{BLUE}────────────────────────────────────────────────────────────────────────{RESET}\n")