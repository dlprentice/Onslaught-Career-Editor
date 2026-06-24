/* address: 0x00407140 */
/* name: CMonitor__RemoveActiveReaderById */
/* signature: void __thiscall CMonitor__RemoveActiveReaderById(void * this, int param_1, int param_2) */


void __thiscall CMonitor__RemoveActiveReaderById(void *this,int param_1,int param_2)

{
  undefined4 *puVar1;
  int *value;

  if (param_1 != 0) {
    puVar1 = *(undefined4 **)((int)this + 0x2a4);
    *(undefined4 **)((int)this + 0x2ac) = puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      value = (int *)0x0;
    }
    else {
      value = (int *)*puVar1;
    }
    if (value != (int *)0x0) {
      while (*value != param_1) {
        puVar1 = *(undefined4 **)(*(int *)((int)this + 0x2ac) + 4);
        *(undefined4 **)((int)this + 0x2ac) = puVar1;
        if (puVar1 == (undefined4 *)0x0) {
          value = (int *)0x0;
        }
        else {
          value = (int *)*puVar1;
        }
        if (value == (int *)0x0) {
          return;
        }
      }
      CSPtrSet__Remove((void *)((int)this + 0x2a4),value);
      if (value != (int *)0x0) {
        CGenericActiveReader__dtor(value);
        OID__FreeObject(value);
      }
    }
  }
  return;
}
