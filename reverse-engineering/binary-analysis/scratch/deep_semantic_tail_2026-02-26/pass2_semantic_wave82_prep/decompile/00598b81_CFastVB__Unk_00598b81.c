/* address: 0x00598b81 */
/* name: CFastVB__Unk_00598b81 */
/* signature: void __fastcall CFastVB__Unk_00598b81(void * param_1) */


void __fastcall CFastVB__Unk_00598b81(void *param_1)

{
  *(undefined ***)param_1 = &PTR_CFastVB__Unk_00598fa4_005ef260;
  if (*(undefined4 **)((int)param_1 + 0x20) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)((int)param_1 + 0x20))(1);
  }
  if (*(undefined4 **)((int)param_1 + 0x24) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)((int)param_1 + 0x24))(1);
  }
  if (*(undefined4 **)((int)param_1 + 0x28) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)((int)param_1 + 0x28))(1);
  }
  if (*(undefined4 **)((int)param_1 + 0x2c) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)((int)param_1 + 0x2c))(1);
  }
  if (*(undefined4 **)((int)param_1 + 0x30) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)((int)param_1 + 0x30))(1);
  }
  OID__FreeObject_Callback(*(void **)((int)param_1 + 0x38));
  CFastVB__Helper_0059871c(param_1);
  return;
}
