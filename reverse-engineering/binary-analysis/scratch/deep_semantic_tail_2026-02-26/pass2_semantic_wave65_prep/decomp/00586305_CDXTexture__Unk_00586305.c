/* address: 0x00586305 */
/* name: CDXTexture__Unk_00586305 */
/* signature: void __thiscall CDXTexture__Unk_00586305(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDXTexture__Unk_00586305(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  short *psVar1;
  undefined4 uVar2;
  float *pfVar3;
  float fVar4;
  short *psVar5;
  void *extraout_ECX;
  short sVar6;
  uint unaff_ESI;

  fVar4 = _DAT_005ea030;
  psVar5 = (short *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                     *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  psVar1 = psVar5 + *(int *)((int)this + 0x1060) * 4;
  pfVar3 = (float *)param_3;
  for (; psVar5 < psVar1; psVar5 = psVar5 + 4) {
    uVar2 = *(undefined4 *)(psVar5 + 2);
    sVar6 = (short)uVar2;
    param_3._0_2_ = (short)((uint)*(undefined4 *)psVar5 >> 0x10);
    *pfVar3 = (float)(int)(short)((ushort)(*psVar5 == -0x8000) + *psVar5) * fVar4;
    pfVar3[1] = (float)(int)(short)((ushort)((short)param_3 == -0x8000) + (short)param_3) * fVar4;
    param_1._0_2_ = (short)((uint)uVar2 >> 0x10);
    pfVar3[2] = (float)(int)(short)((ushort)(sVar6 == -0x8000) + sVar6) * fVar4;
    pfVar3[3] = (float)(int)(short)((ushort)((short)param_1 == -0x8000) + (short)param_1) * fVar4;
    pfVar3 = pfVar3 + 4;
  }
  if (*(int *)((int)this + 0x18) != 0) {
    CFastVB__Helper_00581e1c(this,(int)(pfVar3 + *(int *)((int)this + 0x1060) * -4),unaff_ESI);
    this = extraout_ECX;
  }
  if (*(int *)((int)this + 0x10) != 0) {
    CTexture__Helper_0058210e(this,(int)(pfVar3 + *(int *)((int)this + 0x1060) * -4),unaff_ESI);
  }
  return;
}
