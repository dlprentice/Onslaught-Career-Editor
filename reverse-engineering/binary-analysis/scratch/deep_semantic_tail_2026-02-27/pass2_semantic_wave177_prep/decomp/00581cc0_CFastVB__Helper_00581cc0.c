/* address: 0x00581cc0 */
/* name: CFastVB__Helper_00581cc0 */
/* signature: int __thiscall CFastVB__Helper_00581cc0(void * this, int param_1, int param_2) */


int __thiscall CFastVB__Helper_00581cc0(void *this,int param_1,int param_2)

{
  int iVar1;
  void *extraout_EAX;
  void *pvVar2;

  if ((*(int *)((int)this + 8) != *(int *)(param_1 + 8)) && (*(int *)((int)this + 8) != 4)) {
    *(int *)((int)this + 0x1050) = *(int *)(param_1 + 8);
  }
  if ((*(int *)((int)this + 0x1050) != 0) || (*(int *)((int)this + 0x10) != 0)) {
    iVar1 = *(int *)((int)this + 0x1060);
    OID__AllocObject_DefaultTag_00662b2c(iVar1 << 4);
    if (extraout_EAX == (void *)0x0) {
      pvVar2 = (void *)0x0;
    }
    else {
      _vector_constructor_iterator_(extraout_EAX,0x10,iVar1,CFastVB__ReturnInputInt);
      pvVar2 = extraout_EAX;
    }
    *(void **)((int)this + 0x1054) = pvVar2;
    if (pvVar2 == (void *)0x0) {
      return -0x7ff8fff2;
    }
    if ((*(int *)((int)this + 0x10) != 0) && (*(int *)(param_1 + 0x10) != 0)) {
      *(undefined4 *)(param_1 + 0x14) = 1;
      *(undefined4 *)((int)this + 0x14) = 1;
    }
  }
  return 0;
}
