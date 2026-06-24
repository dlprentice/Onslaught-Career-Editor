/* address: 0x0058cd30 */
/* name: CTexture__Helper_0058cd30 */
/* signature: int __thiscall CTexture__Helper_0058cd30(void * this, void * param_1, void * param_2, void * param_3) */


int __thiscall CTexture__Helper_0058cd30(void *this,void *param_1,void *param_2,void *param_3)

{
  char cVar1;
  void *pvVar2;
  void *this_00;
  uint uVar3;
  int unaff_ESI;
  int iVar4;
  int unaff_EDI;
  char *pcVar5;

  pcVar5 = (char *)((int)param_1 + 2);
  if (((pcVar5 < *(char **)((int)this + 4)) && (*(char *)param_1 == '0')) &&
     (*(char *)((int)param_1 + 1) == 'x')) {
    this_00 = (void *)(int)*pcVar5;
    uVar3 = CRT__IsCharTypeMask0x80(this,this_00,unaff_EDI);
    if (uVar3 != 0) {
      iVar4 = 0;
      for (; pcVar5 < *(char **)((int)this + 4); pcVar5 = pcVar5 + 1) {
        pvVar2 = (void *)(int)*pcVar5;
        uVar3 = CRT__IsCharTypeMask0x80(this_00,(void *)(int)*pcVar5,unaff_ESI);
        this_00 = pvVar2;
        if (uVar3 == 0) break;
        cVar1 = *pcVar5;
        iVar4 = iVar4 * 0x10;
        if (cVar1 < 'a') {
          if (cVar1 < 'A') {
            iVar4 = iVar4 + -0x30 + (int)cVar1;
          }
          else {
            iVar4 = iVar4 + -0x37 + (int)cVar1;
          }
        }
        else {
          iVar4 = iVar4 + -0x57 + (int)cVar1;
        }
      }
      if (param_2 != (void *)0x0) {
        *(int *)param_2 = iVar4;
      }
      iVar4 = (int)pcVar5 - (int)param_1;
      if (iVar4 < 0xb) {
        return iVar4;
      }
      CTexture__Helper_0058c893(*(void **)((int)this + 0x30),(int)this + 8,0x3ea,0x5ea840);
      return iVar4;
    }
  }
  return 0;
}
