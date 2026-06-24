/* address: 0x005893e9 */
/* name: CTexture__IncludeNodeChain_scalar_deleting_dtor */
/* signature: void * __thiscall CTexture__IncludeNodeChain_scalar_deleting_dtor(void * this, void * param_1, int param_2) */


void * __thiscall
CTexture__IncludeNodeChain_scalar_deleting_dtor(void *this,void *param_1,int param_2)

{
  CTexture__FreeChildIncludeNodeChainRecursive((int)this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
