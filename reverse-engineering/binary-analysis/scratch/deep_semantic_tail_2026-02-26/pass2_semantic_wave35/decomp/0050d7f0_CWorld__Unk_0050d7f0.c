/* address: 0x0050d7f0 */
/* name: CWorld__Unk_0050d7f0 */
/* signature: void __fastcall CWorld__Unk_0050d7f0(void * param_1) */


void __fastcall CWorld__Unk_0050d7f0(void *param_1)

{
  undefined4 *puVar1;
  int *obj;

  puVar1 = *(undefined4 **)param_1;
  *(undefined4 **)((int)param_1 + 8) = puVar1;
  if (puVar1 == (undefined4 *)0x0) {
    obj = (int *)0x0;
  }
  else {
    obj = (int *)*puVar1;
  }
  while (obj != (int *)0x0) {
    if (obj != (int *)0x0) {
      if ((undefined4 *)*obj != (undefined4 *)0x0) {
        (*(code *)**(undefined4 **)*obj)(1);
      }
      *obj = 0;
      if ((undefined4 *)obj[1] != (undefined4 *)0x0) {
        (*(code *)**(undefined4 **)obj[1])(1);
      }
      obj[1] = 0;
      OID__FreeObject(obj);
    }
    puVar1 = *(undefined4 **)(*(int *)((int)param_1 + 8) + 4);
    *(undefined4 **)((int)param_1 + 8) = puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      obj = (int *)0x0;
    }
    else {
      obj = (int *)*puVar1;
    }
  }
  CSPtrSet__Clear(param_1);
  return;
}
