/* address: 0x005491b0 */
/* name: CPolyBucket__ReallocFromPool */
/* signature: int __stdcall CPolyBucket__ReallocFromPool(int param_1, int param_2) */


int CPolyBucket__ReallocFromPool(int param_1,int param_2)

{
  char cVar1;
  int iVar2;

  iVar2 = param_2;
  cVar1 = CMemoryManager__ReallocFromPool(param_1,param_2,&param_2);
  if (cVar1 != '\0') {
    return param_2;
  }
  cVar1 = CMemoryManager__ReallocFromPool(param_1,iVar2,&param_2);
  if (cVar1 != '\0') {
    return param_2;
  }
  iVar2 = CMemoryManager__Realloc(param_1 + -0x10,iVar2);
  return iVar2;
}
