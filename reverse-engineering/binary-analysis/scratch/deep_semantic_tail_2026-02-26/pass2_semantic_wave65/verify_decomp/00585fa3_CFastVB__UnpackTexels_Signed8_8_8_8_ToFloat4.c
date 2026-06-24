/* address: 0x00585fa3 */
/* name: CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4 */
/* signature: void __thiscall CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4
          (void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  char cVar3;
  float fVar4;
  undefined4 *puVar5;
  char cVar6;
  char cVar7;
  uint unaff_EDI;

  fVar4 = _DAT_005e9fcc;
  puVar5 = (undefined4 *)
           (*(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
           *(int *)((int)this + 0x20));
  puVar1 = puVar5 + *(int *)((int)this + 0x1060);
  for (; puVar5 < puVar1; puVar5 = puVar5 + 1) {
    uVar2 = *puVar5;
    cVar3 = (char)((uint)uVar2 >> 0x10);
    cVar7 = (char)((uint)uVar2 >> 0x18);
    cVar6 = (char)((uint)uVar2 >> 8);
    *(float *)param_3 = (float)(int)(char)(((char)uVar2 == -0x80) + (char)uVar2) * fVar4;
    *(float *)(param_3 + 4) = (float)(int)(char)((cVar6 == -0x80) + cVar6) * fVar4;
    *(float *)(param_3 + 8) = (float)(int)(char)((cVar3 == -0x80) + cVar3) * fVar4;
    *(float *)(param_3 + 0xc) = (float)(int)(char)((cVar7 == -0x80) + cVar7) * fVar4;
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
