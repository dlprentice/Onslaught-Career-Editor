/* address: 0x004a4e60 */
/* name: CMenuItemRangeVariant__ScalarDestructor */
/* signature: undefined CMenuItemRangeVariant__ScalarDestructor(void) */


void * __thiscall CMenuItemRangeVariant__ScalarDestructor(void *param_1,byte param_2)

{
  CMenuItemRangeVariant__Destructor();
  if ((param_2 & 1) != 0) {
    OID__FreeObject(param_1);
  }
  return param_1;
}
