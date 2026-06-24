/* address: 0x00453a90 */
/* name: FUN_00453a90 */
/* signature: undefined FUN_00453a90(void) */


undefined4 * __thiscall FUN_00453a90(undefined4 *param_1,byte param_2)

{
  *param_1 = &PTR_FUN_005db440;
  if ((param_2 & 1) != 0) {
    OID__FreeObject(param_1);
  }
  return param_1;
}
