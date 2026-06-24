/* address: 0x0058cdd5 */
/* name: CTexture__Helper_0058cdd5 */
/* signature: int __thiscall CTexture__Helper_0058cdd5(void * this, int param_1, void * param_2, void * param_3) */


int __thiscall CTexture__Helper_0058cdd5(void *this,int param_1,void *param_2,void *param_3)

{
  char cVar1;
  bool bVar2;
  uint uVar3;
  int iVar4;
  char *pcVar5;

  if (((uint)param_1 < *(char **)((int)this + 4)) && (*(char *)param_1 == '0')) {
    uVar3 = 0;
    bVar2 = false;
    pcVar5 = (char *)param_1;
    while (((pcVar5 = pcVar5 + 1, pcVar5 < *(char **)((int)this + 4) &&
            (cVar1 = *pcVar5, '/' < cVar1)) && (cVar1 < '8'))) {
      if ((uVar3 & 0xe0000000) != 0) {
        bVar2 = true;
      }
      uVar3 = cVar1 + -0x30 + uVar3 * 8;
    }
    if (param_2 != (void *)0x0) {
      *(uint *)param_2 = uVar3;
    }
    if (bVar2) {
      CTexture__Helper_0058c893(*(void **)((int)this + 0x30),(int)this + 8,0x3eb,0x5ea860);
    }
    iVar4 = (int)pcVar5 - param_1;
  }
  else {
    iVar4 = 0;
  }
  return iVar4;
}
