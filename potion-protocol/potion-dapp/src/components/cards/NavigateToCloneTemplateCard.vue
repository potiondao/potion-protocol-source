<template>
  <CardContainer :fullHeight="false">
    <CardBody class="p-6 text-center">
      <Title label="Not comfortable with custom pools?" />
    </CardBody>
    <CardFooter>
      <Btn
        class="my-1"
        @click="$router.push({ name: 'DiscoverPools' })"
        label="Clone from Template"
        color="secondary-o"
        size="sm"
      />
    </CardFooter>
  </CardContainer>
</template>

<script>
import CardContainer from "@/components/ui/CardContainer.vue";
import CardBody from "@/components/ui/CardBody.vue";
import CardFooter from "@/components/ui/CardFooter.vue";
import Btn from "@/components/ui/Button.vue";
import Title from "@/components/ui/Title.vue";

export default {
  components: {
    CardContainer,
    CardBody,
    CardFooter,
    Btn,
    Title,
  },
};
</script>
