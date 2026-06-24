/* address: 0x0056d18a */
/* name: CDXTexture__Unk_0056d18a */
/* signature: int __cdecl CDXTexture__Unk_0056d18a(int param_1, uint param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl CDXTexture__Unk_0056d18a(int param_1,uint param_2)

{
  int iVar1;

  if ((param_2._2_2_ & 0x7ff0) == 0x7ff0) {
    iVar1 = CFastVB__Unk_00562b3e
                      (param_1,(uint)(CONCAT26(param_2._2_2_,CONCAT24((undefined2)param_2,param_1))
                                     >> 0x20));
    if (iVar1 != 1) {
      if (iVar1 == 2) {
        iVar1 = 4;
      }
      else if (iVar1 == 3) {
        iVar1 = 2;
      }
      else {
        iVar1 = 1;
      }
      return iVar1;
    }
    return 0x200;
  }
  if (((param_2 & 0x7ff00000) == 0) && (((param_2 & 0xfffff) != 0 || (param_1 != 0)))) {
    return (-(uint)((param_2 & 0x80000000) != 0) & 0xffffff90) + 0x80;
  }
  if ((double)CONCAT26(param_2._2_2_,CONCAT24((undefined2)param_2,param_1)) == _DAT_005d87b0) {
    return (-(uint)((param_2 & 0x80000000) != 0) & 0xffffffe0) + 0x40;
  }
  return (-(uint)((param_2 & 0x80000000) != 0) & 0xffffff08) + 0x100;
}
