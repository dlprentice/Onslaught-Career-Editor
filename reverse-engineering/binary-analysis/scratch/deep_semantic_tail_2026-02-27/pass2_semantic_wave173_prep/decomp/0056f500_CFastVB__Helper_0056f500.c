/* address: 0x0056f500 */
/* name: CFastVB__Helper_0056f500 */
/* signature: void __fastcall CFastVB__Helper_0056f500(void * param_1) */


void __fastcall CFastVB__Helper_0056f500(void *param_1)

{
  undefined1 local_1;

  local_1 = (undefined1)((uint)param_1 >> 0x18);
  *(undefined1 *)param_1 = local_1;
  *(undefined4 *)((int)param_1 + 4) = 0;
  *(undefined4 *)((int)param_1 + 8) = 0;
  *(undefined4 *)((int)param_1 + 0xc) = 0;
  return;
}
