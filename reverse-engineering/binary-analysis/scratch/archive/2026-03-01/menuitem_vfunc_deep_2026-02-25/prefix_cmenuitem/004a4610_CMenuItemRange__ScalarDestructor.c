/* address: 0x004a4610 */
/* name: CMenuItemRange__ScalarDestructor */
/* signature: undefined CMenuItemRange__ScalarDestructor(void) */


void * __thiscall CMenuItemRange__ScalarDestructor(void *param_1,byte param_2)

{
  CMenuItemRange__Destructor();
  if ((param_2 & 1) != 0) {
    OID__FreeObject(param_1);
  }
  return param_1;
}
