/* address: 0x0058939b */
/* name: CTexture__IncludeNodeDtor */
/* signature: void * __thiscall CTexture__IncludeNodeDtor(void * this, void * param_1, int param_2) */


void * __thiscall CTexture__IncludeNodeDtor(void *this,void *param_1,int param_2)

{
  CTexture__ReleaseIncludeNodeTreeRecursive((int)this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
