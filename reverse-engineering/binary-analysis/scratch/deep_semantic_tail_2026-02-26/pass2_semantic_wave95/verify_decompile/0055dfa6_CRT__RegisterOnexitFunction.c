/* address: 0x0055dfa6 */
/* name: CRT__RegisterOnexitFunction */
/* signature: int __cdecl CRT__RegisterOnexitFunction(int param_1) */


int __cdecl CRT__RegisterOnexitFunction(int param_1)

{
  int iVar1;

  iVar1 = CRT__OnexitTablePush(param_1);
  return (iVar1 != 0) - 1;
}
