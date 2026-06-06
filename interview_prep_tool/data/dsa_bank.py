"""
DSA problem bank organized by pattern. Each problem carries a name, LeetCode
number/link, difficulty, plain-English approach, tested Python solution, and
complexity. All solutions were run locally before being added.
"""

DSA_PATTERNS = [
    {
        "name": "Real Asked / Target-Company Style",
        "starred": True,
        "problems": [
            {
                "name": "Robot Room Cleaner",
                "lc": 489,
                "url": "https://leetcode.com/problems/robot-room-cleaner/",
                "difficulty": "Hard",
                "approach": (
                    "Blind DFS with backtracking. Track visited cells in a set "
                    "using relative coordinates. After exploring a direction, "
                    "rotate back and step back to undo the move."
                ),
                "code": '''def cleanRoom(robot):
    visited = set()
    # 0:up, 1:right, 2:down, 3:left
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    def go_back():
        robot.turnRight(); robot.turnRight()
        robot.move()
        robot.turnRight(); robot.turnRight()

    def dfs(r, c, d):
        visited.add((r, c))
        robot.clean()
        for i in range(4):
            nd = (d + i) % 4
            nr, nc = r + directions[nd][0], c + directions[nd][1]
            if (nr, nc) not in visited and robot.move():
                dfs(nr, nc, nd)
                go_back()
            robot.turnRight()

    dfs(0, 0, 0)''',
                "complexity": "Time: O(N - M) cells * 4, Space: O(N - M)",
            },
            {
                "name": "Shortest Path in Binary Matrix",
                "lc": 1091,
                "url": "https://leetcode.com/problems/shortest-path-in-binary-matrix/",
                "difficulty": "Medium",
                "approach": "BFS from (0,0) to (n-1,n-1) with 8 directions. Return -1 if blocked.",
                "code": '''from collections import deque
def shortestPathBinaryMatrix(grid):
    n = len(grid)
    if grid[0][0] or grid[n-1][n-1]:
        return -1
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    q = deque([(0, 0, 1)])
    seen = {(0, 0)}
    while q:
        r, c, d = q.popleft()
        if (r, c) == (n-1, n-1):
            return d
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            if 0 <= nr < n and 0 <= nc < n and not grid[nr][nc] and (nr,nc) not in seen:
                seen.add((nr, nc))
                q.append((nr, nc, d+1))
    return -1''',
                "complexity": "Time: O(N^2), Space: O(N^2)",
            },
            {
                "name": "Walls and Gates",
                "lc": 286,
                "url": "https://leetcode.com/problems/walls-and-gates/",
                "difficulty": "Medium",
                "approach": "Multi-source BFS from every gate (0) simultaneously, updating distances.",
                "code": '''from collections import deque
def wallsAndGates(rooms):
    if not rooms: return
    R, C = len(rooms), len(rooms[0])
    q = deque()
    for r in range(R):
        for c in range(C):
            if rooms[r][c] == 0:
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
            nr, nc = r+dr, c+dc
            if 0 <= nr < R and 0 <= nc < C and rooms[nr][nc] == 2147483647:
                rooms[nr][nc] = rooms[r][c] + 1
                q.append((nr, nc))''',
                "complexity": "Time: O(R*C), Space: O(R*C)",
            },
        ],
    },
    {
        "name": "Arrays & Hashing",
        "problems": [
            {
                "name": "Two Sum", "lc": 1,
                "url": "https://leetcode.com/problems/two-sum/",
                "difficulty": "Easy",
                "approach": "Single pass with hashmap of value->index. For each x, look up target-x.",
                "code": '''def twoSum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i''',
                "complexity": "Time: O(N), Space: O(N)",
            },
            {
                "name": "Contains Duplicate", "lc": 217,
                "url": "https://leetcode.com/problems/contains-duplicate/",
                "difficulty": "Easy",
                "approach": "Set length comparison.",
                "code": '''def containsDuplicate(nums):
    return len(set(nums)) != len(nums)''',
                "complexity": "Time: O(N), Space: O(N)",
            },
            {
                "name": "Group Anagrams", "lc": 49,
                "url": "https://leetcode.com/problems/group-anagrams/",
                "difficulty": "Medium",
                "approach": "Bucket by sorted-string or letter-count tuple key.",
                "code": '''from collections import defaultdict
def groupAnagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))
        groups[key].append(s)
    return list(groups.values())''',
                "complexity": "Time: O(N*KlogK), Space: O(N*K)",
            },
            {
                "name": "Top K Frequent Elements", "lc": 347,
                "url": "https://leetcode.com/problems/top-k-frequent-elements/",
                "difficulty": "Medium",
                "approach": "Bucket sort by count to avoid the heap for O(N).",
                "code": '''from collections import Counter
def topKFrequent(nums, k):
    counts = Counter(nums)
    buckets = [[] for _ in range(len(nums)+1)]
    for n, c in counts.items():
        buckets[c].append(n)
    out = []
    for c in range(len(buckets)-1, 0, -1):
        out.extend(buckets[c])
        if len(out) >= k:
            return out[:k]
    return out''',
                "complexity": "Time: O(N), Space: O(N)",
            },
            {
                "name": "Product of Array Except Self", "lc": 238,
                "url": "https://leetcode.com/problems/product-of-array-except-self/",
                "difficulty": "Medium",
                "approach": "Prefix product then suffix multiplied in-place.",
                "code": '''def productExceptSelf(nums):
    n = len(nums)
    out = [1]*n
    p = 1
    for i in range(n):
        out[i] = p
        p *= nums[i]
    p = 1
    for i in range(n-1, -1, -1):
        out[i] *= p
        p *= nums[i]
    return out''',
                "complexity": "Time: O(N), Space: O(1) extra",
            },
        ],
    },
    {
        "name": "Two Pointers",
        "problems": [
            {
                "name": "Valid Palindrome", "lc": 125,
                "url": "https://leetcode.com/problems/valid-palindrome/",
                "difficulty": "Easy",
                "approach": "Two pointers shrinking inward, skip non-alphanumerics, lowercase compare.",
                "code": '''def isPalindrome(s):
    i, j = 0, len(s)-1
    while i < j:
        while i < j and not s[i].isalnum(): i += 1
        while i < j and not s[j].isalnum(): j -= 1
        if s[i].lower() != s[j].lower():
            return False
        i += 1; j -= 1
    return True''',
                "complexity": "Time: O(N), Space: O(1)",
            },
            {
                "name": "3Sum", "lc": 15,
                "url": "https://leetcode.com/problems/3sum/",
                "difficulty": "Medium",
                "approach": "Sort. For each i, two-pointer the remaining for target -nums[i]. Skip duplicates.",
                "code": '''def threeSum(nums):
    nums.sort()
    out = []
    for i in range(len(nums)-2):
        if i > 0 and nums[i] == nums[i-1]: continue
        l, r = i+1, len(nums)-1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s < 0: l += 1
            elif s > 0: r -= 1
            else:
                out.append([nums[i], nums[l], nums[r]])
                while l < r and nums[l] == nums[l+1]: l += 1
                while l < r and nums[r] == nums[r-1]: r -= 1
                l += 1; r -= 1
    return out''',
                "complexity": "Time: O(N^2), Space: O(1) ignoring output",
            },
            {
                "name": "Container With Most Water", "lc": 11,
                "url": "https://leetcode.com/problems/container-with-most-water/",
                "difficulty": "Medium",
                "approach": "Two pointers; always move the shorter wall inward.",
                "code": '''def maxArea(height):
    i, j, best = 0, len(height)-1, 0
    while i < j:
        h = min(height[i], height[j])
        best = max(best, h*(j-i))
        if height[i] < height[j]: i += 1
        else: j -= 1
    return best''',
                "complexity": "Time: O(N), Space: O(1)",
            },
        ],
    },
    {
        "name": "Sliding Window",
        "problems": [
            {
                "name": "Best Time to Buy/Sell Stock", "lc": 121,
                "url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/",
                "difficulty": "Easy",
                "approach": "Track running min, update best = max(best, price-min).",
                "code": '''def maxProfit(prices):
    lo, best = float('inf'), 0
    for p in prices:
        lo = min(lo, p)
        best = max(best, p - lo)
    return best''',
                "complexity": "Time: O(N), Space: O(1)",
            },
            {
                "name": "Longest Substring Without Repeating Characters", "lc": 3,
                "url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
                "difficulty": "Medium",
                "approach": "Window with last-seen index map; advance left to last_seen+1 when collision.",
                "code": '''def lengthOfLongestSubstring(s):
    last = {}
    l = best = 0
    for r, ch in enumerate(s):
        if ch in last and last[ch] >= l:
            l = last[ch] + 1
        last[ch] = r
        best = max(best, r - l + 1)
    return best''',
                "complexity": "Time: O(N), Space: O(min(N, alphabet))",
            },
            {
                "name": "Minimum Window Substring", "lc": 76,
                "url": "https://leetcode.com/problems/minimum-window-substring/",
                "difficulty": "Hard",
                "approach": "Expand right with need-count, shrink left while window covers t. Track best.",
                "code": '''from collections import Counter
def minWindow(s, t):
    if not t or not s: return ""
    need = Counter(t)
    have = {}
    have_n, need_n = 0, len(need)
    l = 0
    res, res_len = (0, 0), float('inf')
    for r, ch in enumerate(s):
        have[ch] = have.get(ch, 0) + 1
        if ch in need and have[ch] == need[ch]:
            have_n += 1
        while have_n == need_n:
            if r - l + 1 < res_len:
                res, res_len = (l, r), r - l + 1
            have[s[l]] -= 1
            if s[l] in need and have[s[l]] < need[s[l]]:
                have_n -= 1
            l += 1
    return s[res[0]:res[1]+1] if res_len != float('inf') else ""''',
                "complexity": "Time: O(N), Space: O(alphabet)",
            },
        ],
    },
    {
        "name": "Stack",
        "problems": [
            {
                "name": "Valid Parentheses", "lc": 20,
                "url": "https://leetcode.com/problems/valid-parentheses/",
                "difficulty": "Easy",
                "approach": "Stack; on close-char, pop and compare.",
                "code": '''def isValid(s):
    pair = {')':'(', ']':'[', '}':'{'}
    st = []
    for ch in s:
        if ch in pair:
            if not st or st.pop() != pair[ch]:
                return False
        else:
            st.append(ch)
    return not st''',
                "complexity": "Time: O(N), Space: O(N)",
            },
            {
                "name": "Daily Temperatures", "lc": 739,
                "url": "https://leetcode.com/problems/daily-temperatures/",
                "difficulty": "Medium",
                "approach": "Monotonic decreasing stack of indices; pop while current is warmer.",
                "code": '''def dailyTemperatures(T):
    out = [0]*len(T)
    st = []
    for i, t in enumerate(T):
        while st and T[st[-1]] < t:
            j = st.pop()
            out[j] = i - j
        st.append(i)
    return out''',
                "complexity": "Time: O(N), Space: O(N)",
            },
        ],
    },
    {
        "name": "Binary Search",
        "problems": [
            {
                "name": "Binary Search", "lc": 704,
                "url": "https://leetcode.com/problems/binary-search/",
                "difficulty": "Easy",
                "approach": "Classic l,r boundaries; mid = (l+r)//2.",
                "code": '''def search(nums, target):
    l, r = 0, len(nums)-1
    while l <= r:
        m = (l+r)//2
        if nums[m] == target: return m
        if nums[m] < target: l = m+1
        else: r = m-1
    return -1''',
                "complexity": "Time: O(logN), Space: O(1)",
            },
            {
                "name": "Search in Rotated Sorted Array", "lc": 33,
                "url": "https://leetcode.com/problems/search-in-rotated-sorted-array/",
                "difficulty": "Medium",
                "approach": "Find which half is sorted, decide where target lies.",
                "code": '''def search(nums, target):
    l, r = 0, len(nums)-1
    while l <= r:
        m = (l+r)//2
        if nums[m] == target: return m
        if nums[l] <= nums[m]:
            if nums[l] <= target < nums[m]: r = m-1
            else: l = m+1
        else:
            if nums[m] < target <= nums[r]: l = m+1
            else: r = m-1
    return -1''',
                "complexity": "Time: O(logN), Space: O(1)",
            },
        ],
    },
    {
        "name": "Linked List",
        "problems": [
            {
                "name": "Reverse Linked List", "lc": 206,
                "url": "https://leetcode.com/problems/reverse-linked-list/",
                "difficulty": "Easy",
                "approach": "Iterative prev/curr/next swap.",
                "code": '''def reverseList(head):
    prev = None
    while head:
        nxt = head.next
        head.next = prev
        prev = head
        head = nxt
    return prev''',
                "complexity": "Time: O(N), Space: O(1)",
            },
            {
                "name": "Merge Two Sorted Lists", "lc": 21,
                "url": "https://leetcode.com/problems/merge-two-sorted-lists/",
                "difficulty": "Easy",
                "approach": "Dummy node + tail pointer.",
                "code": '''def mergeTwoLists(a, b):
    dummy = tail = type('N', (), {'next': None})()
    while a and b:
        if a.val <= b.val:
            tail.next = a; a = a.next
        else:
            tail.next = b; b = b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next''',
                "complexity": "Time: O(N+M), Space: O(1)",
            },
            {
                "name": "Reverse Nodes in k-Group", "lc": 25,
                "url": "https://leetcode.com/problems/reverse-nodes-in-k-group/",
                "difficulty": "Hard",
                "approach": "Walk k ahead; if k nodes exist, reverse the segment, splice back.",
                "code": '''def reverseKGroup(head, k):
    dummy = type('N', (), {'next': head, 'val': 0})()
    group_prev = dummy
    while True:
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if not kth: return dummy.next
        group_next = kth.next
        prev, curr = group_next, group_prev.next
        while curr is not group_next:
            nxt = curr.next
            curr.next = prev
            prev = curr
            curr = nxt
        tmp = group_prev.next
        group_prev.next = kth
        group_prev = tmp''',
                "complexity": "Time: O(N), Space: O(1)",
            },
            {
                "name": "Merge k Sorted Lists", "lc": 23,
                "url": "https://leetcode.com/problems/merge-k-sorted-lists/",
                "difficulty": "Hard",
                "approach": "Min-heap of (val, idx, node); pop smallest, push next.",
                "code": '''import heapq
def mergeKLists(lists):
    heap = []
    for i, n in enumerate(lists):
        if n: heapq.heappush(heap, (n.val, i, n))
    dummy = tail = type('N', (), {'next': None})()
    while heap:
        v, i, n = heapq.heappop(heap)
        tail.next = n
        tail = n
        if n.next:
            heapq.heappush(heap, (n.next.val, i, n.next))
    tail.next = None
    return dummy.next''',
                "complexity": "Time: O(NlogK), Space: O(K)",
            },
            {
                "name": "Copy List with Random Pointer", "lc": 138,
                "url": "https://leetcode.com/problems/copy-list-with-random-pointer/",
                "difficulty": "Medium",
                "approach": "Hashmap old->new; second pass wires next/random.",
                "code": '''def copyRandomList(head):
    mapping = {None: None}
    cur = head
    while cur:
        mapping[cur] = type('N', (), {'val': cur.val, 'next': None, 'random': None})()
        cur = cur.next
    cur = head
    while cur:
        mapping[cur].next = mapping[cur.next]
        mapping[cur].random = mapping[cur.random]
        cur = cur.next
    return mapping[head]''',
                "complexity": "Time: O(N), Space: O(N)",
            },
        ],
    },
    {
        "name": "Trees",
        "problems": [
            {
                "name": "Invert Binary Tree", "lc": 226,
                "url": "https://leetcode.com/problems/invert-binary-tree/",
                "difficulty": "Easy",
                "approach": "Swap children recursively.",
                "code": '''def invertTree(root):
    if not root: return None
    root.left, root.right = invertTree(root.right), invertTree(root.left)
    return root''',
                "complexity": "Time: O(N), Space: O(H)",
            },
            {
                "name": "Maximum Depth of Binary Tree", "lc": 104,
                "url": "https://leetcode.com/problems/maximum-depth-of-binary-tree/",
                "difficulty": "Easy",
                "approach": "1 + max(depth(left), depth(right)).",
                "code": '''def maxDepth(root):
    if not root: return 0
    return 1 + max(maxDepth(root.left), maxDepth(root.right))''',
                "complexity": "Time: O(N), Space: O(H)",
            },
            {
                "name": "Binary Tree Level Order Traversal", "lc": 102,
                "url": "https://leetcode.com/problems/binary-tree-level-order-traversal/",
                "difficulty": "Medium",
                "approach": "BFS by level using queue, append level lists.",
                "code": '''from collections import deque
def levelOrder(root):
    if not root: return []
    q, out = deque([root]), []
    while q:
        level = []
        for _ in range(len(q)):
            n = q.popleft()
            level.append(n.val)
            if n.left: q.append(n.left)
            if n.right: q.append(n.right)
        out.append(level)
    return out''',
                "complexity": "Time: O(N), Space: O(N)",
            },
            {
                "name": "Lowest Common Ancestor (BST)", "lc": 235,
                "url": "https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/",
                "difficulty": "Medium",
                "approach": "Walk down: if both < root go left, if both > root go right, else root.",
                "code": '''def lowestCommonAncestor(root, p, q):
    while root:
        if p.val < root.val and q.val < root.val: root = root.left
        elif p.val > root.val and q.val > root.val: root = root.right
        else: return root''',
                "complexity": "Time: O(H), Space: O(1)",
            },
        ],
    },
    {
        "name": "Heap / Priority Queue",
        "problems": [
            {
                "name": "Kth Largest Element in a Stream", "lc": 703,
                "url": "https://leetcode.com/problems/kth-largest-element-in-a-stream/",
                "difficulty": "Easy",
                "approach": "Min-heap capped at k, peek for kth largest.",
                "code": '''import heapq
class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.h = nums
        heapq.heapify(self.h)
        while len(self.h) > k:
            heapq.heappop(self.h)
    def add(self, val):
        heapq.heappush(self.h, val)
        if len(self.h) > self.k:
            heapq.heappop(self.h)
        return self.h[0]''',
                "complexity": "Time: O(logK) per add, Space: O(K)",
            },
            {
                "name": "Find Median from Data Stream", "lc": 295,
                "url": "https://leetcode.com/problems/find-median-from-data-stream/",
                "difficulty": "Hard",
                "approach": "Two heaps: max-heap for lower half, min-heap for upper half; balance sizes.",
                "code": '''import heapq
class MedianFinder:
    def __init__(self):
        self.lo, self.hi = [], []
    def addNum(self, num):
        heapq.heappush(self.lo, -num)
        heapq.heappush(self.hi, -heapq.heappop(self.lo))
        if len(self.hi) > len(self.lo):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))
    def findMedian(self):
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2''',
                "complexity": "Time: O(logN) per add, Space: O(N)",
            },
        ],
    },
    {
        "name": "Backtracking",
        "problems": [
            {
                "name": "Subsets", "lc": 78,
                "url": "https://leetcode.com/problems/subsets/",
                "difficulty": "Medium",
                "approach": "DFS include/exclude each index.",
                "code": '''def subsets(nums):
    out, path = [], []
    def dfs(i):
        if i == len(nums):
            out.append(path[:]); return
        path.append(nums[i]); dfs(i+1)
        path.pop(); dfs(i+1)
    dfs(0)
    return out''',
                "complexity": "Time: O(2^N * N), Space: O(N) recursion",
            },
            {
                "name": "Combination Sum", "lc": 39,
                "url": "https://leetcode.com/problems/combination-sum/",
                "difficulty": "Medium",
                "approach": "DFS, reuse allowed; advance start index to avoid duplicates.",
                "code": '''def combinationSum(candidates, target):
    out, path = [], []
    def dfs(i, total):
        if total == target:
            out.append(path[:]); return
        if total > target or i >= len(candidates): return
        path.append(candidates[i]); dfs(i, total + candidates[i])
        path.pop(); dfs(i+1, total)
    dfs(0, 0)
    return out''',
                "complexity": "Time: exponential, Space: O(target)",
            },
            {
                "name": "Word Search", "lc": 79,
                "url": "https://leetcode.com/problems/word-search/",
                "difficulty": "Medium",
                "approach": "DFS from each cell; mark visited via temp char swap.",
                "code": '''def exist(board, word):
    R, C = len(board), len(board[0])
    def dfs(r, c, i):
        if i == len(word): return True
        if r<0 or c<0 or r>=R or c>=C or board[r][c] != word[i]: return False
        tmp, board[r][c] = board[r][c], '#'
        found = (dfs(r+1,c,i+1) or dfs(r-1,c,i+1) or
                 dfs(r,c+1,i+1) or dfs(r,c-1,i+1))
        board[r][c] = tmp
        return found
    return any(dfs(r,c,0) for r in range(R) for c in range(C))''',
                "complexity": "Time: O(R*C*4^L), Space: O(L)",
            },
        ],
    },
    {
        "name": "Graphs",
        "problems": [
            {
                "name": "Number of Islands", "lc": 200,
                "url": "https://leetcode.com/problems/number-of-islands/",
                "difficulty": "Medium",
                "approach": "DFS from each '1', flood-fill to '0'.",
                "code": '''def numIslands(grid):
    if not grid: return 0
    R, C = len(grid), len(grid[0])
    def dfs(r, c):
        if r<0 or c<0 or r>=R or c>=C or grid[r][c] != '1': return
        grid[r][c] = '0'
        dfs(r+1,c); dfs(r-1,c); dfs(r,c+1); dfs(r,c-1)
    n = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == '1':
                dfs(r, c); n += 1
    return n''',
                "complexity": "Time: O(R*C), Space: O(R*C)",
            },
            {
                "name": "Clone Graph", "lc": 133,
                "url": "https://leetcode.com/problems/clone-graph/",
                "difficulty": "Medium",
                "approach": "DFS with old->new dict.",
                "code": '''def cloneGraph(node):
    if not node: return None
    old_to_new = {}
    def dfs(n):
        if n in old_to_new: return old_to_new[n]
        copy = type('N', (), {'val': n.val, 'neighbors': []})()
        old_to_new[n] = copy
        for nb in n.neighbors:
            copy.neighbors.append(dfs(nb))
        return copy
    return dfs(node)''',
                "complexity": "Time: O(V+E), Space: O(V)",
            },
            {
                "name": "Course Schedule", "lc": 207,
                "url": "https://leetcode.com/problems/course-schedule/",
                "difficulty": "Medium",
                "approach": "Cycle detection via DFS with 3-color (white/gray/black).",
                "code": '''def canFinish(numCourses, prereqs):
    g = [[] for _ in range(numCourses)]
    for a, b in prereqs:
        g[b].append(a)
    color = [0]*numCourses
    def dfs(u):
        if color[u] == 1: return False
        if color[u] == 2: return True
        color[u] = 1
        for v in g[u]:
            if not dfs(v): return False
        color[u] = 2
        return True
    return all(dfs(i) for i in range(numCourses))''',
                "complexity": "Time: O(V+E), Space: O(V+E)",
            },
        ],
    },
    {
        "name": "Advanced Graphs (Dijkstra / MST)",
        "problems": [
            {
                "name": "Network Delay Time", "lc": 743,
                "url": "https://leetcode.com/problems/network-delay-time/",
                "difficulty": "Medium",
                "approach": "Dijkstra from k; return max dist or -1.",
                "code": '''import heapq
from collections import defaultdict
def networkDelayTime(times, n, k):
    g = defaultdict(list)
    for u, v, w in times:
        g[u].append((v, w))
    dist = {}
    heap = [(0, k)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in dist: continue
        dist[u] = d
        for v, w in g[u]:
            if v not in dist:
                heapq.heappush(heap, (d+w, v))
    return max(dist.values()) if len(dist) == n else -1''',
                "complexity": "Time: O((V+E)logV), Space: O(V+E)",
            },
            {
                "name": "Cheapest Flights Within K Stops", "lc": 787,
                "url": "https://leetcode.com/problems/cheapest-flights-within-k-stops/",
                "difficulty": "Medium",
                "approach": "Bellman-Ford limited to k+1 relaxations.",
                "code": '''def findCheapestPrice(n, flights, src, dst, k):
    INF = float('inf')
    cost = [INF]*n
    cost[src] = 0
    for _ in range(k+1):
        tmp = cost[:]
        for u, v, w in flights:
            if cost[u] + w < tmp[v]:
                tmp[v] = cost[u] + w
        cost = tmp
    return cost[dst] if cost[dst] != INF else -1''',
                "complexity": "Time: O(K*E), Space: O(N)",
            },
        ],
    },
    {
        "name": "1-D Dynamic Programming",
        "problems": [
            {
                "name": "Climbing Stairs", "lc": 70,
                "url": "https://leetcode.com/problems/climbing-stairs/",
                "difficulty": "Easy",
                "approach": "Fib: dp[i]=dp[i-1]+dp[i-2].",
                "code": '''def climbStairs(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a+b
    return a''',
                "complexity": "Time: O(N), Space: O(1)",
            },
            {
                "name": "House Robber", "lc": 198,
                "url": "https://leetcode.com/problems/house-robber/",
                "difficulty": "Medium",
                "approach": "dp[i] = max(dp[i-1], dp[i-2]+nums[i]).",
                "code": '''def rob(nums):
    prev = curr = 0
    for n in nums:
        prev, curr = curr, max(curr, prev + n)
    return curr''',
                "complexity": "Time: O(N), Space: O(1)",
            },
            {
                "name": "Longest Increasing Subsequence", "lc": 300,
                "url": "https://leetcode.com/problems/longest-increasing-subsequence/",
                "difficulty": "Medium",
                "approach": "Patience sorting with bisect.",
                "code": '''from bisect import bisect_left
def lengthOfLIS(nums):
    tails = []
    for x in nums:
        i = bisect_left(tails, x)
        if i == len(tails): tails.append(x)
        else: tails[i] = x
    return len(tails)''',
                "complexity": "Time: O(NlogN), Space: O(N)",
            },
        ],
    },
    {
        "name": "2-D Dynamic Programming",
        "problems": [
            {
                "name": "Unique Paths", "lc": 62,
                "url": "https://leetcode.com/problems/unique-paths/",
                "difficulty": "Medium",
                "approach": "dp[i][j] = dp[i-1][j] + dp[i][j-1]; compress to a row.",
                "code": '''def uniquePaths(m, n):
    row = [1]*n
    for _ in range(m-1):
        for j in range(1, n):
            row[j] += row[j-1]
    return row[-1]''',
                "complexity": "Time: O(M*N), Space: O(N)",
            },
            {
                "name": "Longest Common Subsequence", "lc": 1143,
                "url": "https://leetcode.com/problems/longest-common-subsequence/",
                "difficulty": "Medium",
                "approach": "Standard 2-D DP table on (i, j).",
                "code": '''def longestCommonSubsequence(a, b):
    m, n = len(a), len(b)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m):
        for j in range(n):
            if a[i] == b[j]:
                dp[i+1][j+1] = dp[i][j] + 1
            else:
                dp[i+1][j+1] = max(dp[i+1][j], dp[i][j+1])
    return dp[m][n]''',
                "complexity": "Time: O(M*N), Space: O(M*N)",
            },
        ],
    },
    {
        "name": "Intervals",
        "problems": [
            {
                "name": "Merge Intervals", "lc": 56,
                "url": "https://leetcode.com/problems/merge-intervals/",
                "difficulty": "Medium",
                "approach": "Sort by start; merge if overlap.",
                "code": '''def merge(intervals):
    intervals.sort()
    out = []
    for s, e in intervals:
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out''',
                "complexity": "Time: O(NlogN), Space: O(N)",
            },
            {
                "name": "Non-overlapping Intervals", "lc": 435,
                "url": "https://leetcode.com/problems/non-overlapping-intervals/",
                "difficulty": "Medium",
                "approach": "Sort by end; greedy keep if start >= prev end.",
                "code": '''def eraseOverlapIntervals(intervals):
    intervals.sort(key=lambda x: x[1])
    end = float('-inf')
    kept = 0
    for s, e in intervals:
        if s >= end:
            end = e; kept += 1
    return len(intervals) - kept''',
                "complexity": "Time: O(NlogN), Space: O(1)",
            },
        ],
    },
    {
        "name": "Tries & Greedy",
        "problems": [
            {
                "name": "Implement Trie", "lc": 208,
                "url": "https://leetcode.com/problems/implement-trie-prefix-tree/",
                "difficulty": "Medium",
                "approach": "Dict-of-dicts with end marker.",
                "code": '''class Trie:
    def __init__(self):
        self.root = {}
    def insert(self, w):
        n = self.root
        for c in w:
            n = n.setdefault(c, {})
        n['#'] = True
    def search(self, w):
        n = self.root
        for c in w:
            if c not in n: return False
            n = n[c]
        return '#' in n
    def startsWith(self, p):
        n = self.root
        for c in p:
            if c not in n: return False
            n = n[c]
        return True''',
                "complexity": "Time: O(L) per op, Space: O(N*L)",
            },
            {
                "name": "Jump Game", "lc": 55,
                "url": "https://leetcode.com/problems/jump-game/",
                "difficulty": "Medium",
                "approach": "Track furthest reachable; fail if i exceeds it.",
                "code": '''def canJump(nums):
    far = 0
    for i, x in enumerate(nums):
        if i > far: return False
        far = max(far, i + x)
    return True''',
                "complexity": "Time: O(N), Space: O(1)",
            },
        ],
    },
    {
        "name": "Bit Manipulation",
        "problems": [
            {
                "name": "Single Number", "lc": 136,
                "url": "https://leetcode.com/problems/single-number/",
                "difficulty": "Easy",
                "approach": "XOR all; pairs cancel.",
                "code": '''def singleNumber(nums):
    x = 0
    for n in nums:
        x ^= n
    return x''',
                "complexity": "Time: O(N), Space: O(1)",
            },
            {
                "name": "Number of 1 Bits", "lc": 191,
                "url": "https://leetcode.com/problems/number-of-1-bits/",
                "difficulty": "Easy",
                "approach": "Brian Kernighan: n &= n-1 each iteration.",
                "code": '''def hammingWeight(n):
    c = 0
    while n:
        n &= n - 1
        c += 1
    return c''',
                "complexity": "Time: O(bits set), Space: O(1)",
            },
        ],
    },
    {
        "name": "Matrix",
        "problems": [
            {
                "name": "Rotate Image", "lc": 48,
                "url": "https://leetcode.com/problems/rotate-image/",
                "difficulty": "Medium",
                "approach": "Transpose then reverse each row.",
                "code": '''def rotate(matrix):
    n = len(matrix)
    for i in range(n):
        for j in range(i+1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:
        row.reverse()''',
                "complexity": "Time: O(N^2), Space: O(1)",
            },
            {
                "name": "Spiral Matrix", "lc": 54,
                "url": "https://leetcode.com/problems/spiral-matrix/",
                "difficulty": "Medium",
                "approach": "Shrinking borders; left/right/top/bottom pointers.",
                "code": '''def spiralOrder(matrix):
    out = []
    while matrix:
        out += matrix.pop(0)
        if matrix and matrix[0]:
            for r in matrix:
                out.append(r.pop())
        if matrix:
            out += matrix.pop()[::-1]
        if matrix and matrix[0]:
            for r in matrix[::-1]:
                out.append(r.pop(0))
    return out''',
                "complexity": "Time: O(R*C), Space: O(1) extra",
            },
        ],
    },
]
