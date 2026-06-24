/* address: 0x00407060 */
/* name: CMonitor__Unk_00407060 */
/* signature: void __thiscall CMonitor__Unk_00407060(void * this, int param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CMonitor__Unk_00407060(void *this,int param_1,int param_2)

{
  undefined4 *puVar1;
  float fVar2;
  int *value;
  int *piVar3;

  if (param_1 != 0) {
    puVar1 = *(undefined4 **)((int)this + 0x294);
    *(undefined4 **)((int)this + 0x29c) = puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      value = (int *)0x0;
    }
    else {
      value = (int *)*puVar1;
    }
    if (value != (int *)0x0) {
      while ((DAT_00672fd0 <= (float)value[2] || (*value != param_1))) {
        puVar1 = *(undefined4 **)(*(int *)((int)this + 0x29c) + 4);
        *(undefined4 **)((int)this + 0x29c) = puVar1;
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
      CSPtrSet__Remove((void *)((int)this + 0x294),value);
      puVar1 = *(undefined4 **)((int)this + 0x2a4);
      *(undefined4 **)((int)this + 0x2ac) = puVar1;
      if (puVar1 == (undefined4 *)0x0) {
        piVar3 = (int *)0x0;
      }
      else {
        piVar3 = (int *)*puVar1;
      }
      while( true ) {
        if (piVar3 == (int *)0x0) {
          CSPtrSet__AddToHead((void *)((int)this + 0x2a4),value);
          fVar2 = DAT_00672fd0;
          value[1] = (int)DAT_00672fd0;
          value[2] = (int)(fVar2 + _DAT_005d85ec);
          return;
        }
        if (*piVar3 == param_1) break;
        puVar1 = *(undefined4 **)(*(int *)((int)this + 0x2ac) + 4);
        *(undefined4 **)((int)this + 0x2ac) = puVar1;
        if (puVar1 == (undefined4 *)0x0) {
          piVar3 = (int *)0x0;
        }
        else {
          piVar3 = (int *)*puVar1;
        }
      }
      if (value != (int *)0x0) {
        CGenericActiveReader__dtor(value);
        OID__FreeObject(value);
      }
    }
  }
  return;
}
