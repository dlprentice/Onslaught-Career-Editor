/* address: 0x0047eb00 */
/* name: CHeightField__Unk_0047eb00 */
/* signature: int __fastcall CHeightField__Unk_0047eb00(int param_1, uint param_2, uint param_3) */


int __fastcall CHeightField__Unk_0047eb00(int param_1,uint param_2,uint param_3)

{
  int iVar1;
  int iVar2;

  iVar1 = ((((int)param_2 >> 0xb & 0x3fU) * 0x40 + ((int)param_3 >> 0xb & 0x3fU)) * 9 +
          ((int)param_3 >> 8 & 7U)) * 9 + ((int)param_2 >> 8 & 7U);
  iVar2 = (int)*(short *)(*(int *)(param_1 + 0x1028) + iVar1 * 2);
  iVar1 = *(int *)(param_1 + 0x1028) + iVar1 * 2;
  iVar2 = ((int)((*(short *)(iVar1 + 2) - iVar2) * (param_2 & 0xff)) >> 8) + iVar2;
  return ((int)(((((int)(((int)*(short *)(iVar1 + 0x14) - (int)*(short *)(iVar1 + 0x12)) *
                        (param_2 & 0xff)) >> 8) - iVar2) + (int)*(short *)(iVar1 + 0x12)) *
               (param_3 & 0xff)) >> 8) + iVar2;
}
