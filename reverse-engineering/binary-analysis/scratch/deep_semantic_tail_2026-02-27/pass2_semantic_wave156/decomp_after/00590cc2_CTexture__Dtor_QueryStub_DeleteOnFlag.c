/* address: 0x00590cc2 */
/* name: CTexture__Dtor_QueryStub_DeleteOnFlag */
/* signature: void * __thiscall CTexture__Dtor_QueryStub_DeleteOnFlag(void * this, void * param_1, int param_2) */


void * __thiscall CTexture__Dtor_QueryStub_DeleteOnFlag(void *this,void *param_1,int param_2)

{
  CTexture__SetQueryStubVtableAndReleaseChild(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
