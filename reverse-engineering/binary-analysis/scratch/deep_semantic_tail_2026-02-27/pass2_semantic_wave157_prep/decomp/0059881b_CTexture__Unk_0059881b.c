/* address: 0x0059881b */
/* name: CTexture__Unk_0059881b */
/* signature: int __thiscall CTexture__Unk_0059881b(void * this, void * param_1, int param_2) */


int __thiscall CTexture__Unk_0059881b(void *this,void *param_1,int param_2)

{
  void *pvVar1;
  bool bVar2;
  undefined3 extraout_var;
  uint uVar3;
  int iVar4;
  void *extraout_ECX;
  int unaff_EDI;

  bVar2 = CTexture__HasSameFormatClassId(this,(int)param_1,unaff_EDI);
  iVar4 = 0;
  pvVar1 = extraout_ECX;
  if (CONCAT31(extraout_var,bVar2) != 0) {
    for (; pvVar1 != (void *)0x0; pvVar1 = *(void **)((int)pvVar1 + 0xc)) {
      if (*(int *)((int)pvVar1 + 4) != 1) {
        uVar3 = CTexture__Helper_0059877f(pvVar1,(int)param_1);
        if (uVar3 == 0) {
          return 0;
        }
        break;
      }
      if (param_1 == (void *)0x0) {
        return 0;
      }
      if (*(int *)((int)param_1 + 4) != 1) {
        return 0;
      }
      uVar3 = CTexture__Helper_0059877f(*(void **)((int)pvVar1 + 8),*(int *)((int)param_1 + 8));
      if (uVar3 == 0) {
        return 0;
      }
      param_1 = *(void **)((int)param_1 + 0xc);
    }
    iVar4 = 1;
  }
  return iVar4;
}
