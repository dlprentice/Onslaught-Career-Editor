/* address: 0x005861b4 */
/* name: CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4 */
/* signature: void __thiscall CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Removing unreachable block (ram,0x00586276) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4
          (void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  uint *puVar1;
  float fVar2;
  uint *puVar3;
  void *extraout_ECX;
  short sVar4;
  short sVar5;
  uint unaff_ESI;
  short sVar6;

  fVar2 = _DAT_005ea054;
  puVar3 = (uint *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  puVar1 = puVar3 + *(int *)((int)this + 0x1060);
  for (; puVar3 < puVar1; puVar3 = puVar3 + 1) {
    sVar4 = (short)((ushort)(*puVar3 >> 0x14) << 6) >> 6;
    sVar6 = (short)((short)*puVar3 << 6) >> 6;
    sVar5 = (short)((short)(*puVar3 >> 10) << 6) >> 6;
    *(float *)param_3 = (float)(int)(short)((ushort)(sVar6 == -0x200) + sVar6) * fVar2;
    *(float *)(param_3 + 4) = (float)(int)(short)((ushort)(sVar5 == -0x200) + sVar5) * fVar2;
    *(float *)(param_3 + 8) = (float)(int)(short)((ushort)(sVar4 == -0x200) + sVar4) * fVar2;
    *(float *)(param_3 + 0xc) = (float)(*puVar3 >> 0x1e) * _DAT_005e9f2c;
    param_3 = (int)(param_3 + 0x10);
  }
  if (*(int *)((int)this + 0x18) != 0) {
    CFastVB__Helper_00581e1c(this,(int)(param_3 + *(int *)((int)this + 0x1060) * -4 * 4),unaff_ESI);
    this = extraout_ECX;
  }
  if (*(int *)((int)this + 0x10) != 0) {
    CTexture__Helper_0058210e(this,(int)(param_3 + *(int *)((int)this + 0x1060) * -4 * 4),unaff_ESI)
    ;
  }
  return;
}
