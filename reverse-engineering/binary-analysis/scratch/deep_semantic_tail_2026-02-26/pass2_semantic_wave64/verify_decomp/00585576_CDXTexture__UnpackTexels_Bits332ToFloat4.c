/* address: 0x00585576 */
/* name: CDXTexture__UnpackTexels_Bits332ToFloat4 */
/* signature: void __thiscall CDXTexture__UnpackTexels_Bits332ToFloat4(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDXTexture__UnpackTexels_Bits332ToFloat4
          (void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  float fVar1;
  byte *pbVar2;
  void *extraout_ECX;
  uint unaff_EDI;
  byte *pbVar3;

  fVar1 = _DAT_005e9f38;
  pbVar2 = (byte *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  pbVar3 = pbVar2 + *(int *)((int)this + 0x1060);
  for (; pbVar2 < pbVar3; pbVar2 = pbVar2 + 1) {
    *(float *)param_3 = (float)(*pbVar2 >> 5) * fVar1;
    *(float *)(param_3 + 4) = (float)(*pbVar2 >> 2 & 7) * fVar1;
    *(float *)(param_3 + 8) = (float)(*pbVar2 & 3) * _DAT_005e9f2c;
    *(float *)(param_3 + 0xc) = 1.0;
    param_3 = (int)(param_3 + 0x10);
  }
  if (*(int *)((int)this + 0x18) != 0) {
    CFastVB__Helper_00581e1c(this,(int)(param_3 + *(int *)((int)this + 0x1060) * -4 * 4),unaff_EDI);
    this = extraout_ECX;
  }
  if (*(int *)((int)this + 0x10) != 0) {
    CTexture__Helper_0058210e(this,(int)(param_3 + *(int *)((int)this + 0x1060) * -4 * 4),unaff_EDI)
    ;
  }
  return;
}
