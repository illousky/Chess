<template>
  <div class="py-5"></div>
  <div>
    <h1>FAQ</h1>

    <p class="mt-4">
      <strong>How can players update the result of a game?</strong>
      <span :class="{ show: showMore1 }" class="more-text">
        <br><br>
        Go to the tournament page, open the "pairing/results" tab, provide the Lichess game ID in the input field (for Lichess games) or select the result from the dropdown list (for OTB games) and then click on the icon. 
      </span>
    </p>
    <button @click="toggle('1')" id="faq1" class="faq-button btn btn-primary rounded-pill shadow-sm">
      {{ showMore1 ? 'Read less' : 'Read more' }}
    </button>

    <p class="mt-4">
      <strong>How can administrators add players to a tournament?</strong>
      <span :class="{ show: showMore2 }" class="more-text">
        <br><br>
        Players are added using the CSV file format. Comma-separated values (CSV) is a text format that uses commas to separate values, and newlines to separate records. The first row of the CSV file must contain the column names.             
        <br><br>
        The column names must match the fields of the player. The most common fields are: name, email, lichess_username.
        <br><br>
        For Lichess tournaments, the lichess_username is required. For OTB tournaments, the name and email are required.
        <br><br>
        For Lichess tournaments, the lichess_username will be checked against the Lichess database and the player's rating will be retrieved. For OTB tournaments, the email will be used as the user password.
        <br><br>
        Example Lichess tournament:<br>
        <code>
          lichess_username<br>
          username1<br>
          username2<br>
          username3<br>
        </code>
        <br><br>
        Example OTB tournament:<br>
        <code>
          name, email<br>
          name1, name1@gmail.com<br>
          name2, name2@gmail.com<br>
          name3, name3@gmail.com<br> 
        </code>       
      </span>
    </p>
    <button @click="toggle('2')" id="faq2" class="faq-button btn btn-primary rounded-pill shadow-sm">
      {{ showMore2 ? 'Read less' : 'Read more' }}
    </button>
  </div>
</template>

<script setup>

  import { ref } from 'vue';

  const showMore1 = ref(false);
  const showMore2 = ref(false);

  function toggle(id) {
    if (id === '1') {
      showMore1.value = !showMore1.value;
    } else if (id === '2') {
      showMore2.value = !showMore2.value;
    }
  }

</script>

<style scoped>

  .more-text {
    display: none;
    opacity: 0;
    transition: opacity 0.4s ease;
  }

  .more-text.show {
    display: inline;
    opacity: 1;
  }

  .faq-button {
    margin-top: 10px;
    padding: 6px 14px;
    font-size: 16px;
  }
  
</style>
