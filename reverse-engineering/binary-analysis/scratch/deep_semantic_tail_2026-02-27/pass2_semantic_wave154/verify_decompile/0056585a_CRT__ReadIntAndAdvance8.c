/* address: 0x0056585a */
/* name: CRT__ReadIntAndAdvance8 */
/* signature: int __cdecl CRT__ReadIntAndAdvance8(void * param_1) */


int __cdecl CRT__ReadIntAndAdvance8(void *param_1)

{
  *(int *)param_1 = *(int *)param_1 + 8;
  return *(int *)(*(int *)param_1 + -8);
}
