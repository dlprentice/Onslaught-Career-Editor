/* address: 0x00533430 */
/* name: IScript__ScalarDeletingDestructor */
/* signature: void * __thiscall IScript__ScalarDeletingDestructor(void * this, void * param_1, int param_2) */


void * __thiscall IScript__ScalarDeletingDestructor(void *this,void *param_1,int param_2)

{
  IScript__ctor_like_00533450(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject(this);
  }
  return this;
}
