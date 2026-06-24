/* address: 0x0058210e */
/* name: CTexture__Helper_0058210e */
/* signature: void __thiscall CTexture__Helper_0058210e(void * this, int param_1, uint param_2) */


void __thiscall CTexture__Helper_0058210e(void *this,int param_1,uint param_2)

{
  float *pfVar1;
  uint uVar2;
  int iVar3;
  undefined2 in_FPUControlWord;
  double dVar4;
  undefined4 local_c;

  uVar2 = *(int *)((int)this + 0x1060) * 0x10 + param_1;
  if (*(int *)((int)this + 0x14) == 0) {
    local_c = CONCAT22(local_c._2_2_,in_FPUControlWord);
    DAT_009d0c58 = local_c;
    if ((*(int *)((int)this + 8) == 1) || (*(int *)((int)this + 8) == 4)) {
      if ((uint)param_1 < uVar2) {
        iVar3 = ((uVar2 - param_1) - 1 >> 4) + 1;
        pfVar1 = (float *)(param_1 + 8);
        do {
          dVar4 = CFastVB__Helper_00581a08(pfVar1[-2]);
          pfVar1[-2] = (float)dVar4;
          dVar4 = CFastVB__Helper_00581a08(pfVar1[-1]);
          pfVar1[-1] = (float)dVar4;
          dVar4 = CFastVB__Helper_00581a08(*pfVar1);
          *pfVar1 = (float)dVar4;
          pfVar1 = pfVar1 + 4;
          iVar3 = iVar3 + -1;
        } while (iVar3 != 0);
      }
    }
    else if ((uint)param_1 < uVar2) {
      iVar3 = ((uVar2 - param_1) - 1 >> 4) + 1;
      pfVar1 = (float *)(param_1 + 0xc);
      do {
        dVar4 = CFastVB__Helper_00581a08(*pfVar1);
        *pfVar1 = (float)dVar4;
        pfVar1 = pfVar1 + 4;
        iVar3 = iVar3 + -1;
      } while (iVar3 != 0);
    }
  }
  else if ((*(int *)((int)this + 8) == 1) || (*(int *)((int)this + 8) == 4)) {
    if ((uint)param_1 < uVar2) {
      pfVar1 = (float *)(param_1 + 8);
      iVar3 = ((uVar2 - param_1) - 1 >> 4) + 1;
      do {
        pfVar1[-2] = pfVar1[-2] * pfVar1[-2];
        pfVar1[-1] = pfVar1[-1] * pfVar1[-1];
        *pfVar1 = *pfVar1 * *pfVar1;
        pfVar1 = pfVar1 + 4;
        iVar3 = iVar3 + -1;
      } while (iVar3 != 0);
    }
  }
  else if ((uint)param_1 < uVar2) {
    pfVar1 = (float *)(param_1 + 0xc);
    iVar3 = ((uVar2 - param_1) - 1 >> 4) + 1;
    do {
      *pfVar1 = *pfVar1 * *pfVar1;
      pfVar1 = pfVar1 + 4;
      iVar3 = iVar3 + -1;
    } while (iVar3 != 0);
  }
  return;
}
