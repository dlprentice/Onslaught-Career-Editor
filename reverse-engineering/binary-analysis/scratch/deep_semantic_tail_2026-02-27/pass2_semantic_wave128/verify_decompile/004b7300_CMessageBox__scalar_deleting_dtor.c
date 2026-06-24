/* address: 0x004b7300 */
/* name: CMessageBox__scalar_deleting_dtor */
/* signature: void * __thiscall CMessageBox__scalar_deleting_dtor(void * this, void * param_1, int param_2) */


void * __thiscall CMessageBox__scalar_deleting_dtor(void *this,void *param_1,int param_2)

{
  CMessageBox__ctor_like_004b7930(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject(this);
  }
  return this;
}
