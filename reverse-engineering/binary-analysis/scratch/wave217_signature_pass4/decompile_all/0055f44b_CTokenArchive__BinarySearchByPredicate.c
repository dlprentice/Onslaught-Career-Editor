/* address: 0x0055f44b */
/* name: CTokenArchive__BinarySearchByPredicate */
/* signature: uint __cdecl CTokenArchive__BinarySearchByPredicate(int search_key, uint base_offset, uint item_count, int item_stride, void * predicate) */


uint __cdecl
CTokenArchive__BinarySearchByPredicate
          (int search_key,uint base_offset,uint item_count,int item_stride,void *predicate)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;

  uVar4 = (item_count - 1) * item_stride + base_offset;
  if (base_offset <= uVar4) {
    do {
      uVar3 = item_count >> 1;
      if (uVar3 == 0) {
        if (item_count == 0) {
          return 0;
        }
        iVar2 = (*predicate)(search_key,base_offset);
        return ~-(uint)(iVar2 != 0) & base_offset;
      }
      uVar1 = uVar3;
      if ((item_count & 1) == 0) {
        uVar1 = uVar3 - 1;
      }
      uVar1 = uVar1 * item_stride + base_offset;
      iVar2 = (*predicate)(search_key,uVar1);
      if (iVar2 == 0) {
        return uVar1;
      }
      if (iVar2 < 0) {
        uVar4 = uVar1 - item_stride;
        if ((item_count & 1) == 0) {
          uVar3 = uVar3 - 1;
        }
      }
      else {
        base_offset = uVar1 + item_stride;
      }
      item_count = uVar3;
    } while (base_offset <= uVar4);
  }
  return 0;
}
