/* address: 0x00586438 */
/* name: CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ */
/* signature: void __thiscall CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ
          (void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  char *pcVar1;
  char cVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  char *pcVar6;
  uint unaff_EDI;

  fVar5 = _DAT_005e9fcc;
  pcVar6 = (char *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  pcVar1 = pcVar6 + *(int *)((int)this + 0x1060) * 2;
  for (; pcVar6 < pcVar1; pcVar6 = pcVar6 + 2) {
    cVar2 = pcVar6[1];
    fVar3 = (float)(int)(char)((*pcVar6 == -0x80) + *pcVar6) * fVar5;
    *(float *)param_3 = fVar3;
    fVar4 = (float)(int)(char)((cVar2 == -0x80) + cVar2) * fVar5;
    *(float *)(param_3 + 4) = fVar4;
    fVar3 = (_DAT_005e6a34 - fVar3 * fVar3) - fVar4 * fVar4;
    if (fVar3 < DAT_005e6a3c == (fVar3 == DAT_005e6a3c)) {
      fVar3 = SQRT(fVar3);
    }
    else {
      fVar3 = 0.0;
    }
    *(float *)(param_3 + 8) = fVar3;
    *(float *)(param_3 + 0xc) = 1.0;
    param_3 = param_3 + 0x10;
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
