/* address: 0x0058aa69 */
/* name: CTexture__HandleDirective_IfdefIfndef */
/* signature: int __thiscall CTexture__HandleDirective_IfdefIfndef(void * this, int param_1, void * param_2) */


int __thiscall CTexture__HandleDirective_IfdefIfndef(void *this,int param_1,void *param_2)

{
  int iVar1;
  void *local_8;

  local_8 = this;
  iVar1 = CTexture__FindMacroSymbol((void *)param_1,&param_1,&local_8);
  if (iVar1 == 0) {
LAB_0058aab3:
    iVar1 = 0;
  }
  else {
    if (param_1 == 0) {
      if (local_8 == (void *)0x0) goto LAB_0058aab3;
      if (((*(int *)((int)local_8 + 0xc) == 0) && (1 < *(int *)((int)local_8 + 0x10))) &&
         (*(int *)((int)local_8 + 0x10) < 5)) {
        return *(int *)((int)local_8 + 0x18);
      }
    }
    else {
      CTexture__Helper_0058c893((void *)((int)this + 4),(int)this + 0x60,0x5ed,0x5ea560);
    }
    iVar1 = 1;
  }
  return iVar1;
}
