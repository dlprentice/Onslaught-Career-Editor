/* address: 0x00585e9f */
/* name: CDXTexture__Unk_00585e9f */
/* signature: void __thiscall CDXTexture__Unk_00585e9f(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDXTexture__Unk_00585e9f(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  char *pcVar1;
  float fVar2;
  char *pcVar3;
  char cVar4;
  uint unaff_EDI;

  fVar2 = _DAT_005e9fcc;
  pcVar3 = (char *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  pcVar1 = pcVar3 + *(int *)((int)this + 0x1060) * 4;
  for (; pcVar3 < pcVar1; pcVar3 = pcVar3 + 4) {
    cVar4 = (char)((uint)*(undefined4 *)pcVar3 >> 8);
    *(float *)param_3 = (float)(int)(char)((*pcVar3 == -0x80) + *pcVar3) * fVar2;
    *(float *)(param_3 + 4) = (float)(int)(char)((cVar4 == -0x80) + cVar4) * fVar2;
    *(float *)(param_3 + 8) = 1.0;
    *(float *)(param_3 + 0xc) = (float)(byte)pcVar3[2] * _DAT_005e9ee0;
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
