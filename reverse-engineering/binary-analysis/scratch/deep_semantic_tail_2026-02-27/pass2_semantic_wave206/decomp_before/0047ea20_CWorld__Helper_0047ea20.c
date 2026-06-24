/* address: 0x0047ea20 */
/* name: CWorld__Helper_0047ea20 */
/* signature: uint __fastcall CWorld__Helper_0047ea20(int param_1, uint param_2, uint param_3) */


uint __fastcall CWorld__Helper_0047ea20(int param_1,uint param_2,uint param_3)

{
  int iVar1;

  if (((param_2 | param_3) & 0x3ffe00) == 0) {
    iVar1 = ((((int)param_2 >> 3 & 0x3fU) * 0x40 + ((int)param_3 >> 3 & 0x3fU)) * 9 + (param_3 & 7))
            * 9 + (param_2 & 7);
    return CONCAT22((short)((uint)iVar1 >> 0x10),
                    *(undefined2 *)(*(int *)(param_1 + 0x1028) + iVar1 * 2));
  }
  if ((param_2 & 0x3ffe00) == 0x200) {
    if ((param_3 & 0x3ffe00) == 0x200) {
      return CONCAT22((short)((uint)*(int *)(param_1 + 0x1028) >> 0x10),
                      *(undefined2 *)(*(int *)(param_1 + 0x1028) + 0xa1ffe));
    }
    return CONCAT22((short)((uint)*(int *)(param_1 + 0x1028) >> 0x10),
                    *(undefined2 *)
                     (*(int *)(param_1 + 0x1028) + 0x9f790 +
                     (((int)param_3 >> 8 & 0x3fU) * 9 + (param_3 & 7)) * 0x12));
  }
  if ((param_3 & 0x3ffe00) == 0x200) {
    iVar1 = ((int)param_2 >> 3 & 0x3fU) * 0x1440 + (param_2 & 7);
    return CONCAT22((short)((uint)iVar1 >> 0x10),
                    *(undefined2 *)(*(int *)(param_1 + 0x1028) + 0x286e + iVar1 * 2));
  }
  return param_3 & 0x3f0000;
}
