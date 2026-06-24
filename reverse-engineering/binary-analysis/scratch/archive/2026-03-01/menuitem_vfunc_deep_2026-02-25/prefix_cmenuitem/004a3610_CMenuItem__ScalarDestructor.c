/* address: 0x004a3610 */
/* name: CMenuItem__ScalarDestructor */
/* signature: undefined CMenuItem__ScalarDestructor(void) */


void * __thiscall CMenuItem__ScalarDestructor(void *param_1,byte param_2)

{
  CMenuItem__Destructor();
  if ((param_2 & 1) != 0) {
    OID__FreeObject(param_1);
  }
  return param_1;
}
