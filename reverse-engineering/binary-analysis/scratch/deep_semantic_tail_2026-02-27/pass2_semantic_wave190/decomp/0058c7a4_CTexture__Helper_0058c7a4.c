/* address: 0x0058c7a4 */
/* name: CTexture__Helper_0058c7a4 */
/* signature: int __thiscall CTexture__Helper_0058c7a4(void * this, int param_1, void * param_2, void * param_3) */


int __thiscall CTexture__Helper_0058c7a4(void *this,int param_1,void *param_2,void *param_3)

{
  bool bVar1;
  bool bVar2;
  int iVar3;
  char *pcVar4;

  bVar2 = false;
  bVar1 = false;
  pcVar4 = (char *)param_1;
  if ((uint)param_1 < *(uint *)((int)this + 4)) {
    do {
      if (bVar1) {
LAB_0058c7dd:
        if (bVar2) break;
        iVar3 = CRT__ToLower_005695af((int)*pcVar4);
        if (iVar3 != 0x6c) break;
        bVar2 = true;
      }
      else {
        iVar3 = CRT__ToLower_005695af((int)*pcVar4);
        if (iVar3 != 0x75) goto LAB_0058c7dd;
        bVar1 = true;
      }
      pcVar4 = pcVar4 + 1;
    } while (pcVar4 < *(char **)((int)this + 4));
  }
  if (param_2 != (void *)0x0) {
    if (bVar1) {
      *(undefined4 *)param_2 = 4;
    }
    else if (bVar2) {
      *(undefined4 *)param_2 = 3;
    }
  }
  return (int)pcVar4 - param_1;
}
