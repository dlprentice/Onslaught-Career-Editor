/* address: 0x004f7460 */
/* name: CUnit__Unk_004f7460 */
/* signature: void __thiscall CUnit__Unk_004f7460(void * this, void * param_1, void * param_2) */


void __thiscall CUnit__Unk_004f7460(void *this,void *param_1,void *param_2)

{
  int iVar1;
  int iVar2;
  void *unaff_EDI;
  void *pvVar3;

  iVar2 = *(int *)((int)this + 0xc);
  pvVar3 = *(void **)((int)this + 4);
  do {
    if (iVar2 == 0) {
LAB_004f748d:
      iVar2 = *(int *)((int)this + 8);
      iVar1 = *(int *)this;
      *(undefined4 *)(iVar1 + iVar2 * 8) = *(undefined4 *)param_1;
      *(undefined4 *)(iVar1 + 4 + iVar2 * 8) = *(undefined4 *)((int)param_1 + 4);
      *(int *)((int)this + 8) = *(int *)((int)this + 8) + 1;
      return;
    }
    iVar1 = CUnit__Unk_004f74b0(this,pvVar3,param_1,unaff_EDI);
    if (iVar1 != 0) {
      if (iVar2 != 0) {
        return;
      }
      goto LAB_004f748d;
    }
    pvVar3 = (void *)((int)pvVar3 + 6);
    iVar2 = iVar2 + -1;
  } while( true );
}
