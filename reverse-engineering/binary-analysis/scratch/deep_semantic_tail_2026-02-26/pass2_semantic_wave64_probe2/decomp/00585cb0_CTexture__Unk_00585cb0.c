/* address: 0x00585cb0 */
/* name: CTexture__Unk_00585cb0 */
/* signature: void __thiscall CTexture__Unk_00585cb0(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CTexture__Unk_00585cb0(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  char *pcVar1;
  char cVar2;
  float fVar3;
  char *pcVar4;
  uint unaff_EDI;

  fVar3 = _DAT_005e9fcc;
  pcVar4 = (char *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  pcVar1 = pcVar4 + *(int *)((int)this + 0x1060) * 2;
  for (; pcVar4 < pcVar1; pcVar4 = pcVar4 + 2) {
    cVar2 = pcVar4[1];
    *(float *)param_3 = (float)(int)(char)((*pcVar4 == -0x80) + *pcVar4) * fVar3;
    *(float *)(param_3 + 4) = (float)(int)(char)((cVar2 == -0x80) + cVar2) * fVar3;
    *(float *)(param_3 + 8) = 1.0;
    *(float *)(param_3 + 0xc) = 1.0;
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
