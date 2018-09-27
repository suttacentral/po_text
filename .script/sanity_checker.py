import regex

from common import PO_DIR, pofile, humansortkey


class Num:
    def __init__(self, string):
        if '-' in string:
            self.start, self.end = [int(num) for num in string.split('-')]
        else:
            self.start = self.end = int(string)
    
    def __repr__(self):
        if self.start == self.end:
            return str(self.start)
        return f'{self.start}-{self.end}'
    
    

def is_1_greater(a, b, uid, original_con):
    ones_count = 0
    
    if len(b) > len(a):
        a += [Num('0')]

    for i in range(0, min(len(a), len(b))):
        num_a = a[i]
        num_b = b[i]
        
        diff = num_b.start - num_a.end
        if diff == 1:
            ones_count += 1
    if ones_count != 1:
        if original_con.endswith('.0a'):
            return
        print(f"{uid}:{original_con}   {'.'.join(str(n) for n in a)} -> {'.'.join(str(n) for n in b)}")
        return False

def renumber_zeros(po):
    i = 1
    for unit in po.units:
        msgctxt = unit.msgctxt
        if not msgctxt:
            continue
        uid, num = msgctxt[0][1:-1].split(':')
        
        if num.startswith('0'):
            unit.msgctxt[0] = f'"{uid}:0.{i}"'
            i += 1
        else:
            return i > 1

def renumber_segments(po):
    changed = False
    last_nums = None
    inc = 1
    for unit in po.units:
        msgctxt = unit.msgctxt
        if not msgctxt:
            continue
        uid, num = msgctxt[0][1:-1].split(':')
        
        nums = num.split('.')
        
        if last_nums and len(last_nums) == 3:
            if nums[:2] == last_nums[:2]:
                m = regex.match(r'(\d+)([a-z]*)', last_nums[2])
                last_num, last_alpha = m[1], m[2]
                m = regex.match(r'(\d+)([a-z]*)', nums[2])
                num, alpha = m[1], m[2]
                
                if alpha:
                    continue
                
                new_num = str(int(last_num) + 1)
                if new_num != nums[2]:
                    nums[2] = new_num
                    new_ctxt = f'"{uid}:{".".join(nums)}"'
                    if msgctxt[0] != new_ctxt:
                        print(f'Replace: {msgctxt[0]} -> {new_ctxt}, {msgctxt[0] == new_ctxt}')
                        unit.msgctxt = [new_ctxt]
                        changed = True
        last_nums = nums
    return changed
            
            
            
            
        

def compare_order(a, b):
    nums_a = [l[1] for l in a]
    nums_b = [l[1] for l in b]
    if nums_a == nums_b:
        return False
    for i, j in zip(nums_a, nums_b):
        if i != j:
            print(f'{a[0][0]}: Sort Mismatch {i} != {j}')
            return



def check_ordering(contexts, file):
    
    compare_order(contexts, sorted(contexts, key=humansortkey))
    compare_order(contexts, sorted(reversed(contexts), key=humansortkey))
    

for file in sorted(PO_DIR.glob('pli-tv/**/*.po')):
    with file.open('r') as f:
        po = pofile(f)  
    
    changed = False
    if 'np' in file.name:
        changed = renumber_zeros(po)
    
    changed = renumber_segments(po) or changed 
    
    contexts = []
    for unit in po.units:    
        msgctxt = unit.msgctxt
        if msgctxt:
            contexts.append(msgctxt[0][1:-1].split(':'))
    
    
    check_ordering(contexts, file)
    
    file_uid = regex.sub(r'(\D)(0+)', r'\1', file.stem)
    nums = []
    last_nums = None
    for uid, con in contexts:
        if file_uid != uid:
            print(f'Mismatched UID: {uid} in {file_uid}')
        
        con2 = regex.sub(r'[a-z]$', lambda m: '.'+str(ord(m[0])-96), con )
        nums = [Num(num) for num in con2.split('.')]
        if last_nums is not None:
            is_1_greater(last_nums, nums, uid, con)
            
        
        last_nums = nums
    if changed:
        po.save()
