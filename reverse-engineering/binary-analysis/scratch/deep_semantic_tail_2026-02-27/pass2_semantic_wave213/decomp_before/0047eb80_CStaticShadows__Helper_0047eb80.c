/* address: 0x0047eb80 */
/* name: CStaticShadows__Helper_0047eb80 */
/* signature: double __fastcall CStaticShadows__Helper_0047eb80(int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CStaticShadows__Helper_0047eb80(int param_1,void *param_2)

{
  float fVar1;
  float fVar2;
  int iVar3;
  int iVar4;

  fVar1 = (*(float *)param_2 - _DAT_005dbdf0) + _DAT_005dbdec;
  fVar2 = (*(float *)((int)param_2 + 4) - _DAT_005dbdf0) + _DAT_005dbdec;
  if ((((uint)fVar2 | (uint)fVar1) & 0x3e0000) == 0) {
    iVar3 = ((((int)fVar1 >> 0xb & 0x3fU) * 0x40 + ((int)fVar2 >> 0xb & 0x3fU)) * 9 +
            ((int)fVar2 >> 8 & 7U)) * 9 + ((int)fVar1 >> 8 & 7U);
    iVar4 = (int)*(short *)(*(int *)(param_1 + 0x1028) + iVar3 * 2);
    iVar3 = *(int *)(param_1 + 0x1028) + iVar3 * 2;
    iVar4 = ((int)((*(short *)(iVar3 + 2) - iVar4) * ((uint)fVar1 & 0xff)) >> 8) + iVar4;
    return (double)((float)(((int)(((((int)(((int)*(short *)(iVar3 + 0x14) -
                                            (int)*(short *)(iVar3 + 0x12)) * ((uint)fVar1 & 0xff))
                                     >> 8) - iVar4) + (int)*(short *)(iVar3 + 0x12)) *
                                  ((uint)fVar2 & 0xff)) >> 8) + iVar4) *
                   *(float *)(param_1 + 0x102c));
  }
  return (double)_DAT_005d856c;
}
