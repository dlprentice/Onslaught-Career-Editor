/* address: 0x00453a90 */
/* name: CMenuItem__scalar_deleting_dtor */
/* signature: undefined CMenuItem__scalar_deleting_dtor(void) */


undefined4 * __thiscall CMenuItem__scalar_deleting_dtor(undefined4 *param_1,byte param_2)

{
  *param_1 = &PTR_CMenuItem__scalar_deleting_dtor_005db440;
  if ((param_2 & 1) != 0) {
    OID__FreeObject(param_1);
  }
  return param_1;
}
