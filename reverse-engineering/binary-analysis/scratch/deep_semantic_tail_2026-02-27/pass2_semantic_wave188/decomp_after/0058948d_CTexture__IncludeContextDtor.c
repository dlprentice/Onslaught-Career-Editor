/* address: 0x0058948d */
/* name: CTexture__IncludeContextDtor */
/* signature: void * __thiscall CTexture__IncludeContextDtor(void * this, void * param_1, int param_2) */


void * __thiscall CTexture__IncludeContextDtor(void *this,void *param_1,int param_2)

{
  CTexture__CleanupIncludeContextRecursive((int)this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
