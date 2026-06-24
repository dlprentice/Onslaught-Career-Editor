/* address: 0x00428e80 */
/* name: VFuncSlot_04_00428e80 */
/* signature: void __fastcall VFuncSlot_04_00428e80(void * param_1) */


void __fastcall VFuncSlot_04_00428e80(void *param_1)

{
  if ((*(int *)((int)param_1 + 0xc) != 0) &&
     ((*(byte *)(*(int *)((int)param_1 + 0xc) + 0x2c) & 4) != 0)) {
    CGenericActiveReader__SetReader((void *)((int)param_1 + 0xc),(void *)0x0);
  }
  (**(code **)(*(int *)param_1 + 0x2c))();
  return;
}
