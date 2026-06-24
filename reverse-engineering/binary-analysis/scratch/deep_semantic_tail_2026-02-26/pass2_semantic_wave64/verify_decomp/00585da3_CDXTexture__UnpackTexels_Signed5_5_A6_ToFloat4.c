/* address: 0x00585da3 */
/* name: CDXTexture__UnpackTexels_Signed5_5_A6_ToFloat4 */
/* signature: void __thiscall CDXTexture__UnpackTexels_Signed5_5_A6_ToFloat4(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDXTexture__UnpackTexels_Signed5_5_A6_ToFloat4
          (void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  ushort *puVar1;
  float fVar2;
  ushort *puVar3;
  char cVar4;
  char cVar5;
  uint unaff_EDI;

  fVar2 = _DAT_005e9f28;
  puVar3 = (ushort *)
           (*(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
           *(int *)((int)this + 0x20));
  puVar1 = puVar3 + *(int *)((int)this + 0x1060);
  for (; puVar3 < puVar1; puVar3 = puVar3 + 1) {
    cVar5 = (char)((char)*puVar3 << 3) >> 3;
    cVar4 = (char)((char)(*puVar3 >> 5) << 3) >> 3;
    *(float *)param_3 = (float)(int)(char)((cVar5 == -0x10) + cVar5) * fVar2;
    *(float *)(param_3 + 4) = (float)(int)(char)((cVar4 == -0x10) + cVar4) * fVar2;
    *(float *)(param_3 + 8) = 1.0;
    *(float *)(param_3 + 0xc) = (float)(*puVar3 >> 10) * _DAT_005e9ef4;
    param_3 = (int)(param_3 + 0x10);
  }
  if (*(int *)((int)this + 0x18) != 0) {
    CFastVB__Helper_00581e1c(this,(int)(param_3 + *(int *)((int)this + 0x1060) * -4 * 4),unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    CTexture__Helper_0058210e(this,(int)(param_3 + *(int *)((int)this + 0x1060) * -4 * 4),unaff_EDI)
    ;
  }
  return;
}
