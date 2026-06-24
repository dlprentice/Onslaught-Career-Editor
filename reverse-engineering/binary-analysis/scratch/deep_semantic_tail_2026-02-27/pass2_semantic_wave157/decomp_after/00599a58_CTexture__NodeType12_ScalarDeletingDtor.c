/* address: 0x00599a58 */
/* name: CTexture__NodeType12_ScalarDeletingDtor */
/* signature: void * __thiscall CTexture__NodeType12_ScalarDeletingDtor(void * this, void * param_1, int param_2) */


void * __thiscall CTexture__NodeType12_ScalarDeletingDtor(void *this,void *param_1,int param_2)

{
  CTexture__Helper_005999b5(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
